# -*- coding:utf-8 -*-

import email
from phen.event import Event
from phen.util import path_join as pj


class Flags:
    # from http://cr.yp.to/proto/maildir.html
    passed = "P"    # the user has resent/forwarded/bounced this message.
    replied = "R"   # the user has replied to this message.
    seen = "S"      # the user has viewed this message.
    trashed = "T"   # the user has moved this message to the trash.
    draft = "D"     # the user considers this message a draft.
    flagged = "F"   # user-defined flag; toggled at user discretion.


stored_headers = (  # from thunderbird/icedove
    'FROM', 'TO', 'CC', 'BCC', 'SUBJECT', 'DATE', 'MESSAGE-ID',
    'PRIORITY', 'X-PRIORITY', 'REFERENCES', 'NEWSGROUPS', 'IN-REPLY-TO',
    'CONTENT-TYPE', 'REPLY-TO'
)


class Message:
    __slots__ = "fname".split()

    def __init__(self, fname):
        self.fname = fname

    def get_flags(self):
        parts = self.fname.split(":2,")
        return parts and parts[-1]

    def change_flags(self, box, flags, op):
        base, cur_flags = self.fname.split(":2,", 1)
        if op == 1:
            for flag in flags:
                if flag and flag not in cur_flags:
                    cur_flags += flag
            cur_flags = "".join(sorted(cur_flags))
        elif op == -1:
            for flag in flags:
                if flag:
                    cur_flags = cur_flags.replace(flag, '')
        newname = ":2,".join((base, cur_flags))
        if newname == self.fname:
            return
        path = box._mpj(self.fname)
        newpath = box._mpj(newname)
        box.ignore = True  # ignore folder change notification
        box.ctx.fs.rename(path, newpath)
        self.fname = newname

    def expunge(self, box):
        if Flags.trashed in self.get_flags():
            box.ctx.fs.unlink(box._mpj(self.fname))
            return True

    def __contains__(self, flag):
        return flag in self.get_flags()

    def get_uid(self, box):
        path = box._mpj(self.fname)
        xattr = box.ctx.fs.xattr(path)
        if "uid" not in xattr:
            xattr["uid"] = box.next_uid(True)
            box.ignore = True
            box.ctx.fs.xattr(path, xattr)
        return xattr["uid"]

    def get_date(self, box):
        path = box._mpj(self.fname)
        return box.ctx.fs.filemeta(path).dtime

    def get_size(self, box, zeroTrashed=False):
        path = box._mpj(self.fname)
        if zeroTrashed and Flags.trashed in self.get_flags():
            return 0
        return box.ctx.fs.filemeta(path).size

    def get_headers(self, box, full=False):
        # todo: cache stuff from the last msg in box
        path = box._mpj(self.fname)
        #
        with box.ctx.fs.open(path, "rd") as in_:
            msg = email.message_from_string(in_.read())
        return msg
        #
        xattr = box.ctx.fs.xattr(path)
        if "headers" not in xattr:
            from . import dict_headers
            with box.ctx.fs.open(path, "rd") as in_:
                msg = email.message_from_string(in_.read())
            xattr["headers"] = h = dict_headers(msg, full and stored_headers)
            box.ignore = True
            box.ctx.fs.xattr(path, xattr)
            box.ctx.fs.utime(path, h.get("Date", 0))
        return xattr["headers"]

    def get_message(self, box, raw=False):
        path = box._mpj(self.fname)
        with box.ctx.fs.open(path, "rd") as in_:
            data = in_.read()
        import six
        if six.PY3:
            data = data.decode("latin1")
        if raw:
            return data
        return email.message_from_string(data)

    def get_part(self, box, part_idx=None):
        msg = self.get_message(box)
        if part_idx is not None:
            return msg.get_payload(part_idx)
        return msg.get_payload()

    def is_multipart(self, box):
        from pprint import pprint
        pprint(self.get_headers(box))
        return "multipart" in self.get_headers(box).get("Content-Type", [])


class MailBox:
    def __init__(self, ctx, path):
        self.ctx = ctx
        self.path = path
        msg_path = pj(self.path, "cur")
        if not self.ctx.fs.exists(msg_path):
            self.ctx.fs.mkdir(msg_path)
        self.__folder = ctx.fs.traverse(msg_path)[0][-1]
        self.ignore = False
        self.ctx.fs.folder_modified.subscribe(self._folder_modified)
        self._messages = None
        self._messages_by_uid = None
        self.load()
        self.changed = Event()

    def _folder_modified(self, folder, notif_tag, external):
        try:
            if folder == self.__folder:
                if self.ignore:
                    self.ignore = False
                    return
                self.load_messages()
                self.changed(self)
        except:
            pass

    def _mpj(self, fname):
        return pj(self.path, "cur", fname)

    @property
    def messages(self):
        if self._messages is None:
            self.load_messages()
        return self._messages

    @property
    def messages_by_uid(self):
        if self._messages is None:
            self.load_messages()
        return self._messages_by_uid

    def msn_msg_by_uid(self, uid):
        msg = self._messages_by_uid.get(uid)
        if msg:
            return self.messages.index(msg), msg
        return None, None

    def load_messages(self):
        self._messages = []
        self._messages_by_uid = {}
        for fname in self.__folder.listdir():
            msg = Message(fname)
            self._messages_by_uid[msg.get_uid(self)] = msg
            self._messages.append(msg)

    def load(self):
        try:
            self.state = self.ctx.fs.xattr(self.path)
        except IOError:
            self.state = {}

    def save(self):
        self.ctx.fs.xattr(self.path, self.state)

    def subscribed(self, change=None):
        retv = self.state.setdefault("subscribed", True)
        if change is not None:
            self.state["subscribed"] = change
            self.save()
        return retv

    def next_uid(self, inc=False):
        retv = self.state.setdefault("next_uid", 1)
        if inc:
            self.state["next_uid"] = retv + 1
            self.save()
        return retv

    def uid_validity(self, invalidate=False):
        retv = self.state.get("uid_validity")
        if retv is None or invalidate:
            self.state["uid_validity"] = retv = (retv or 42 ** 5) + 1
            self.save()
        return retv

    def recent_uid(self, mark=False):
        if mark:
            retv = self.state["next_uid"]
            if self.state.get("recent_uid") != retv:
                self.state["recent_uid"] = retv
                self.save()
        else:
            retv = self.state.get("recent_uid")
        return retv or self.next_uid()

    def get_uid(self, msn):
        self.messages[msn].get_uid(self)

    def message_count(self):
        return len(self.messages)

    def recent_count(self):
        return sum(
            1 for uid in range(self.recent_uid(), self.next_uid())
            if uid in self.messages_by_uid
        )

    def unseen_count(self):
        return sum(1 for m in self.messages if 'S' not in m)

    def add(self, msg_file, flags="", date=None):
        import time
        import random
        flags = "".join(sorted(f for f in flags if f))
        name = "{}.{:05.0f}:2,{}".format(
            time.time(), random.random() * 10 ** 5, flags
        )
        path = self._mpj(name)
        self.ignore = True
        with self.ctx.fs.open(path, "wd") as out:
            out.write(msg_file.read())
        uid = self.next_uid(True)
        self.ctx.fs.xattr(path, {"uid": uid})
        if date:
            self.ctx.fs.utime(path, date)
        msg = Message(name)
        self.messages.append(msg)
        self.messages_by_uid[uid] = msg
        self.__folder.flush()

    def expunge(self):
        retv = [i for i, msg in enumerate(self.messages) if msg.expunge(self)]
        self.__folder.flush()
        return retv
