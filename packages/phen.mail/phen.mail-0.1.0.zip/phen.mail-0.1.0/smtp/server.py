# -*- coding:utf-8 -*-

from twisted.mail import smtp
from twisted.cred import portal, checkers
from zope.interface import implementer
from twisted.mail.imap4 import LOGINCredentials, PLAINCredentials

from ..common.checker import Avatar, Checker


@implementer(smtp.IMessageDelivery)
class Delivery:
    def __init__(self, plugin, avatar):
        self.plugin = plugin
        self.avatar = avatar

    def validateFrom(self, helo, origin):
        self.origin = origin
        if self.avatar.external_MDA:
            if str(origin) == self.address:
                return origin
            cmd_def = self.plugin.get_user_folder(str(origin))
            if not cmd_def or cmd_def != self.external_MDA:
                raise smtp.SMTPBadSender(origin, resp="Invalid alias")
        if self.avatar.is_anonynous:
            if origin.domain in self.plugin.config.get("domains", []):
                raise smtp.SMTPBadSender(
                    origin, resp="Unauthenticated senders not allowed"
                )
            return origin
        if str(origin) == self.avatar.username:
            return origin
        folder = self.plugin.get_user_folder(str(origin))
        if folder != self.avatar.folder:
            raise smtp.SMTPBadSender(origin, resp="Invalid alias")
        return origin

    def validateTo(self, user):
        from . import relay
        domains = self.plugin.config.get("domains", [])
        relaying = self.plugin.relay_manager or self.plugin.config("hosted")
        # check if relaying
        if user.dest.domain not in domains:
            if self.avatar.is_anonynous or not relaying:
                raise smtp.SMTPBadRcpt(user, resp="Relaying denied")
            return lambda: relay.Message(self.origin, str(user.dest))
        elif user.dest.local not in domains[user.dest.domain]:
            raise smtp.SMTPBadRcpt(user, resp="Address unknown")
        folder = self.plugin.get_user_folder(str(user))
        if not folder:
            raise smtp.SMTPBadRcpt(user)
        # local delivery
        from ..delivery import message
        if folder[0] == ">":
            cmd = folder[1:].format(FROM=self.origin).rsplit(" ", 1)[0]
            if "@" in cmd.split()[0]:
                return lambda: relay.Message(self.origin, cmd)
            return lambda: message.ExternalMDA(cmd)
        elif folder[0] == ".":
            return lambda: message.Plugin(folder[1:], self.origin)
        dest = Avatar()
        dest.get_config(folder)
        if dest.external_MDA:
            if dest.ctx.account != 'admin':
                # external - but user configured - must verify config
                user_cmd = dest.idhash + dest.external_MDA
                admin_auth = dest.cfg.get("authorization", "")
                from phen.context import device
                if not device.cid.verify(user_cmd, admin_auth):
                    # need authorization to run external commands
                    raise smtp.SMTPBadRcpt(user)
            dest.shutdown()
            cmd = dest.external_MDA.format(FROM=self.origin)
            if "@" in cmd.split()[0]:
                return lambda: relay.Message(self.origin, cmd)
            return lambda: message.ExternalMDA(cmd)
        return lambda: message.Local(dest)


@implementer(portal.IRealm)
class Realm:
    def __init__(self, plugin):
        self.plugin = plugin

    def requestAvatar(self, avatar, mind, *ifaces):
        if smtp.IMessageDelivery in ifaces:
            delivery = Delivery(self.plugin, avatar or Avatar())
            return smtp.IMessageDelivery, delivery, lambda: None
        else:
            raise Exception("No supported interfaces found.")


class ESMTP(smtp.ESMTP):
    max_size = 0

    def extensions(self):
        ext = {'AUTH': self.challengers.keys(), 'SIZE': str(self.max_size)}
        if self.canStartTLS and not self.startedTLS:
            ext['STARTTLS'] = None
        return ext

    def receivedHeader(self, helo, origin, recipients):
        heloStr = ""
        if helo[0]:
            heloStr = " helo=%s" % (helo[0],)
        domain = self.transport.getHost().host
        from_ = "from %s ([%s]%s)" % (helo[0], helo[1], heloStr)
        by = "by %s with ESMTP%s" % (domain, "S" if self.startedTLS else "")
        for_ = "for %s; %s" % (
            ' '.join(map(str, recipients)), smtp.rfc822date()
        )
        return "Received: %s\n\t%s\n\t%s" % (from_, by, for_)


class Factory(smtp.SMTPFactory):
    protocol = ESMTP

    def __init__(self, plugin, max_size):
        ESMTP.max_size = max_size
        self.plugin = plugin
        self.domain = self.plugin.sender_domain.encode("latin1")
        self.portal = portal.Portal(Realm(plugin))
        self.portal.registerChecker(Checker(plugin, True))
        self.portal.registerChecker(checkers.AllowAnonymousAccess())
        from phen.util.ssl import get_ctx
        self.ssl_ctx_factory = get_ctx()

    def buildProtocol(self, addr):
        p = smtp.SMTPFactory.buildProtocol(self, addr)
        p.challengers = dict(LOGIN=LOGINCredentials, PLAIN=PLAINCredentials)
        p.ctx = self.ssl_ctx_factory
        return p
