# -*- coding:utf-8 -*-

import os
from twisted.mail import imap4
from twisted.cred import portal
from twisted.internet import reactor

from ..common.checker import Checker
from .server import Realm, Factory, IMAP4Debug


def setup(plugin, cfg):
    debug = cfg.get("debug", False)
    Factory.protocol = IMAP4Debug if debug else imap4.IMAP4Server
    Factory.portal = portal.Portal(Realm())
    Factory.portal.registerChecker(Checker(plugin))

    factory = Factory()

    host = cfg.get("host", "0.0.0.0")
    port = cfg.get("port", None)
    if cfg.get("disable-ssl", False):
        if port is None:
            port = 2143 if os.getuid() else 143
        return reactor.listenTCP(int(port), factory, interface=host)
    else:
        if port is None:
            port = 2993 if os.getuid() else 993
        from phen.util.ssl import get_ctx
        return reactor.listenSSL(int(port), factory, get_ctx(), interface=host)
