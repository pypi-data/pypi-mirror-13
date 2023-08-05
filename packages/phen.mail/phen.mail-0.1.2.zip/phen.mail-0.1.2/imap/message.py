# -*- coding:utf-8 -*-

import six
from io import BytesIO
from twisted.mail import imap4
from email.utils import formatdate
from zope.interface import implementer


Maildir_to_IMAP = dict(
    P=r"$Forwarded",
    S=r"\Seen",
    R=r"\Answered",
    F=r"\Flagged",
    T=r"\Deleted",
    D=r"\Draft",
    a=r"$Junk",
    b=r"$NonJunk",
    c=r"$Spam",
    d=r"$NonSpam"
)
IMAP_to_Maildir = {v[1:].lower(): k for k, v in Maildir_to_IMAP.items()}


@implementer(imap4.IMessagePart)
class MessagePart:
    def __init__(self, mime_msg):
        self.msg = mime_msg

    def getHeaders(self, negate, *names):
        names = set(n.lower() for n in names)
        return {
            k.lower().encode("latin1"): v.encode("latin1")
            for k, v in self.msg.items()
            if (k.lower() not in names) == negate
        }

    def as_file(self, start, length):
        retv = self.msg.as_string()
        if length:
            retv = retv[start:start + length]
        if six.PY3:
            retv = retv.encode("latin1")
        return BytesIO(retv)

    def getBodyFile(self, start=0, length=0):
        if self.isMultipart():
            retv = "".join(
                part.as_string() for part in self.msg.get_part(self.box)
            )
        else:
            retv = self.msg.get_payload()
        if length:
            retv = retv[start:start + length]
        if six.PY3:
            retv = retv.encode("latin1")
        return BytesIO(retv)

    def getSize(self):
        return len(self.msg.as_string())

    def getInternalDate(self):
        return ""

    def isMultipart(self):
        retv = self.msg.is_multipart()
        return retv

    def getSubPart(self, part_idx):
        return MessagePart(self.msg.get_payload(part_idx))


@implementer(imap4.IMessage)
class Message:
    def __init__(self, box, msg):
        self.box = box
        self.msg = msg

    def getUID(self):
        return self.msg.get_uid(self.box)

    def getFlags(self):
        uid = self.msg.get_uid(self.box)
        flags = [
            Maildir_to_IMAP[f]
            for f in self.msg.get_flags()
            if f in Maildir_to_IMAP
        ]
        if uid >= self.box.recent_uid():
            flags.append(r"\Recent")
        return flags

    def change_flags(self, flags, op):
        flags = (IMAP_to_Maildir.get(flag[1:].lower()) for flag in flags)
        self.msg.change_flags(self.box, flags, op)

    def getInternalDate(self):
        date = self.msg.get_date(self.box)
        return formatdate(date)

    def getHeaders(self, negate, *names):
        names = set(n.lower() for n in names)
        headers = self.msg.get_headers(self.box)
        # date = headers.pop("Date", None)
        # if date is not None:
        #     headers["Date"] = formatdate(date)
        retv = {
            k.lower(): (
                "\r\n".join(v) if isinstance(v, list) else v
            )
            for k, v in headers.items()
            if (k.lower() not in names) == negate
        }
        return retv

    def as_file(self, start, length):
        retv = self.msg.get_message(self.box).as_string()
        if length:
            retv = retv[start:start + length]
        if six.PY3:
            retv = retv.encode("latin1")
        return BytesIO(retv)

    def getBodyFile(self, start=0, length=0):
        if self.isMultipart():
            retv = "".join(
                part.as_string() for part in self.msg.get_part(self.box)
            )
        else:
            retv = self.msg.get_part(self.box)
        if length:
            retv = retv[start:start + length]
        if six.PY3:
            retv = retv.encode("latin1")
        return BytesIO(retv)

    def getSize(self):
        return self.msg.get_size(self.box)

    def isMultipart(self):
        retv = self.msg.is_multipart(self.box)
        return retv

    def getSubPart(self, part_idx):
        return MessagePart(self.msg.get_part(self.box, part_idx))
