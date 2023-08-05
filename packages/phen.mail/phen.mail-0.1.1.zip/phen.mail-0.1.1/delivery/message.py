# -*- coding:utf-8 -*-

from twisted.mail import smtp
from twisted.internet import defer
from zope.interface import implementer

from phen.plugin import Manager
from ..smtp.server import ESMTP


@implementer(smtp.IMessage)
class Base:
    def __init__(self):
        from io import BytesIO
        self.buffer = BytesIO()

    def lineReceived(self, line):
        self.buffer.write(line + "\n")
        if ESMTP.max_size and self.buffer.tell() > ESMTP.max_size:
            raise smtp.SMTPServerError(552, "Message exceeds allowed size")

    def connectionLost(self):
        self.buffer = None


class Local(Base):
    def __init__(self, avatar):
        Base.__init__(self)
        self.avatar = avatar

    def eomReceived(self):
        if not hasattr(self.avatar, "delivery"):
            from .process import Delivery
            self.avatar.delivery = Delivery(self.avatar)
        self.avatar.delivery.process(self.buffer)
        self.buffer = None
        return defer.succeed(None)


class Plugin(Base):
    def __init__(self, calldef, origin):
        Base.__init__(self)
        self.origin = origin
        if " " in calldef:
            self.name, self.param = calldef.split(" ", 1)
        else:
            self.name, self.param = calldef, None

    def eomReceived(self):
        if self.name not in Manager.singleton:
            # todo: bounce
            return defer.succeed(None)
        wrapper = Manager.singleton[self.name]
        import email
        msg = email.message_from_string(self.buffer.getvalue())
        wrapper.call("mail_received", msg, self.origin, self.param)
        self.buffer = None
        return defer.succeed(None)


class ExternalMDA(Base):
    def __init__(self, command):
        Base.__init__(self)
        self.cmd = command

    def eomReceived(self):
        import subprocess
        # note: command comes from device config or from an authorized
        # user config (signed by the device identity)
        proc = subprocess.Popen(self.cmd, shell=True, stdin=subprocess.PIPE)
        proc.communicate(self.buffer.getvalue())
        self.buffer = None
        return defer.succeed(None)
