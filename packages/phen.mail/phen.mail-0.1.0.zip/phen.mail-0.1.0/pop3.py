# -*- coding:utf-8 -*-

import os
from io import BytesIO
from twisted.mail import pop3
from twisted.cred import portal
from zope.interface import implementer
from twisted.internet import reactor, protocol

from .common import mailbox, checker


@implementer(pop3.IMailbox)
class Mailbox:
    loginDelay = 1
    messageExpiration = 365

    def __init__(self, avatar):
        avatar.ctx.fs.chdir(avatar.folder)
        self.box = mailbox.MailBox(avatar.ctx, u".Inbox")

    def listMessages(self, idx=None):
        if idx is not None:
            return self.box.messages[idx].get_size(self.box, True)
        return [msg.get_size(self.box, True) for msg in self.box.messages]

    def getMessage(self, idx):
        return BytesIO(self.box.messages[idx].get_message(self.box, True))

    def getUidl(self, idx):
        return self.box.messages[idx].get_uid(self.box)

    def deleteMessage(self, idx):
        self.box.messages[idx].change_flags(self.box, mailbox.Flags.trashed, 1)

    def undeleteMessages(self):
        for msg in self.box.messages:
            msg.change_flags(self.box, mailbox.Flags.trashed, -1)

    def sync(self):
        self.box.expunge()


@implementer(portal.IRealm)
class Realm:
    def requestAvatar(self, avatar, mind, *ifaces):
        if pop3.IMailbox in ifaces:
            return pop3.IMailbox, Mailbox(avatar), avatar.shutdown
        else:
            raise Exception("No supported interfaces found.")


class Factory(protocol.ServerFactory):
    def __init__(self, plugin):
        self.portal = portal.Portal(Realm())
        self.portal.registerChecker(checker.Checker(plugin))

    def buildProtocol(self, address):
        p = pop3.POP3()
        p.portal = self.portal
        return p


def setup(plugin, cfg):
    factory = Factory(plugin)
    host = cfg.get("host", "0.0.0.0")
    port = cfg.get("port", None)
    if cfg.get("disable-ssl", False):
        if port is None:
            port = 2110 if os.getuid() else 110
        return reactor.listenTCP(int(port), factory, interface=host)
    if port is None:
        port = 2995 if os.getuid() else 995
    from phen.util.ssl import get_ctx
    return reactor.listenSSL(int(port), factory, get_ctx(), interface=host)
