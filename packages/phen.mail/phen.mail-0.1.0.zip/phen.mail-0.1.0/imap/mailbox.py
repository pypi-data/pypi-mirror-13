# -*- coding:utf-8 -*-

from twisted.mail import imap4
from twisted.internet import defer
from zope.interface import implementer

from .message import Message, IMAP_to_Maildir
from ..common import mailbox


@implementer(imap4.IMailbox, imap4.ICloseableMailbox)
class MailBox(object):

    flags = (
        r"\Seen \Answered \Flagged \Deleted "
        r"\Draft \Recent $Forwarded $Junk $NonJunk $Spam $NonSpam".split()
    )
    folder_flags = r"\Trash \Junk \Sent \Drafts".split()
    messages = []
    mUID = 0
    rw = 1
    closed = False

    @property
    def box(self):
        """Lazy-loader for the actual box"""
        if self._box is None:
            self._box = mailbox.MailBox(self.account.ctx, self.path)
            self._box.changed.subscribe(self.box_changed)
        return self._box

    def __init__(self, account, path):
        self.account = account
        self.path = path
        self._box = None
        self.listeners = set()

    def box_changed(self, box):
        for listener in self.listeners:
            listener.newMessages(box.message_count(), box.recent_count())

    def getFlags(self):
        special = "\\" + self.path.split(".")[-1].capitalize()
        if special in self.folder_flags:
            return self.flags + [special.encode()]
        return self.flags

    def getHierarchicalDelimiter(self):
        return '/'

    def getUIDValidity(self):
        return self.box.uid_validity()

    def getUIDNext(self):
        return self.box.next_uid()

    def getUID(self, message):
        return self.box.get_uid(message)

    def getMessageCount(self):
        return self.box.message_count()

    def getRecentCount(self):
        return self.box.recent_count()

    def getUnseenCount(self):
        return self.box.unseen_count()

    def isWriteable(self):
        return True

    def destroy(self):
        if self._box:
            self._box.changed.unsubscribe(self.box_changed)

    def requestStatus(self, names):
        return imap4.statusRequestHelper(self, names)

    def addListener(self, listener):
        self.listeners.add(listener)

    def removeListener(self, listener):
        self.listeners.discard(listener)

    def addMessage(self, message, flags, date=None):
        if date is not None:
            import calendar
            from email.utils import parsedate_tz
            date = calendar.timegm(parsedate_tz(date))
        flags = (IMAP_to_Maildir.get(flag[1:].lower()) for flag in flags)
        self.box.add(message, flags, date)
        return defer.succeed(True)

    def expunge(self):
        return self.box.expunge()

    def fetch(self, messages, uid):
        retv = []  # retv must be a list; generator screws search
        if uid:
            if not messages.last:
                messages.last = self.box.next_uid()
            for uid in messages:
                msn, msg = self.box.msn_msg_by_uid(uid)
                if msn is not None:
                    retv.append((msn + 1, Message(self.box, msg)))
        else:
            if not messages.last:
                messages.last = self.box.message_count()
            for msn in messages:
                try:
                    msg = self.box.messages[msn - 1]
                    retv.append((msn, Message(self.box, msg)))
                except IndexError:
                    pass
            retv.sort(key=lambda o: o[1].getUID())
        self.box.recent_uid(True)
        return retv

    def store(self, messages, flags, mode, uid):
        for num, msg in self.fetch(messages, uid):
            msg.change_flags(flags, mode)

    def close(self):
        self.closed = True
