# -*- coding:utf-8 -*-

import re
import errno
from twisted.mail import imap4
from zope.interface import implementer

from .mailbox import MailBox


def wildcardToRegex(wildcard):
    wildcard = wildcard.replace('*', '(?:.*?)')
    wildcard = wildcard.replace('%', '(?:(?:[^/])*?)')
    return re.compile(wildcard, re.I)


@implementer(imap4.IAccount, imap4.INamespacePresenter)
class Account:
    def __init__(self, ctx, path):
        self.ctx = ctx
        self.path = path
        self.mailboxes = {}
        self.scan_mailbox(path, u"")

    def scan_mailbox(self, path, mail_path):
        for name in self.ctx.fs.listdir(path):
            if name.startswith("."):
                child_p = u"/".join((path, name))
                child_mp = mail_path + name[1:]
                try:
                    self.scan_mailbox(child_p, child_mp + u"/")
                except IOError as exc:
                    if exc.args[0] == errno.ENOTDIR:
                        continue
                self.mailboxes[child_mp.upper()] = (
                    child_mp, MailBox(self, child_p)
                )

    def _all_descendants(self, name):
        descendants = []
        for desc_name in self.mailboxes.keys():
            if desc_name.upper().startswith(name):
                descendants.append(desc_name)
        return descendants

    def listMailboxes(self, ref, wildcard):
        ref = self._all_descendants(ref.upper())
        wildcard = wildcardToRegex(wildcard)
        return [self.mailboxes[i] for i in ref if wildcard.match(i)]

    def select(self, path, rw=True):
        mbox = self.mailboxes.get(path.decode().upper())
        return mbox and mbox[1]

    def isSubscribed(self, path):
        mbox = self.mailboxes.get(path.decode().upper())
        return mbox and mbox[1].box.subscribed()

    def subscribe(self, path):
        mbox = self.mailboxes.get(path.decode().upper())
        if mbox:
            mbox[1].box.subscribed(True)
        return True

    def unsubscribe(self, path):
        mbox = self.mailboxes.get(path.decode().upper())
        if mbox:
            mbox[1].box.subscribed(False)
        return True

    def close(self):
        return True

    def create(self, path):
        parts = ["." + p for p in path.decode().split("/")]
        parent = u"/".join(parts[:-1])
        if not parent or self.ctx.fs.exists(parent):
            child = u"/".join([self.path] + parts)
            self.ctx.fs.mkdir(child)
            self.mailboxes[path.upper()] = path, MailBox(self, child)
            return True

    def delete(self, path):
        mbox = self.mailboxes.pop(path.decode().upper())
        self.ctx.fs.rmtree(mbox[1].path)

    def rename(self, oldname, newname):
        mbox = self.mailboxes.pop(oldname.decode().upper())
        parts = newname.decode().split("/")
        if len(parts) == 1:
            parent = u"."
        else:
            pmbox = self.mailboxes.get(u"/".join(parts[:-1]).upper())
            parent = pmbox and pmbox[1].path
        if parent:
            dest = u"/.".join((parent, parts[-1]))
            self.ctx.fs.rename(mbox[1].path, dest)
            self.mailboxes[newname.upper()] = newname, mbox[1]
        else:
            # cancel
            self.mailboxes[oldname.decode().upper()] = mbox

    def getPersonalNamespaces(self):
        return [["", "/"]]

    def getSharedNamespaces(self):
        return None

    def getOtherNamespaces(self):
        return None
