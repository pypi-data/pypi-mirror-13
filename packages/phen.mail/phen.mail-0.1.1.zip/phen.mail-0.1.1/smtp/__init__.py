# -*- coding:utf-8 -*-

import os
from twisted.internet import reactor
from . import server


def setup(plugin, cfg):
    factory = server.Factory(plugin, cfg.get("max-size", 0))
    p1, p2 = None, None
    if not cfg.get("only-relay", False):
        host = cfg.get("host", "0.0.0.0")
        port = cfg.get("port", None)
        if port is None:
            port = 2025 if os.getuid() else 25
        p1 = reactor.listenTCP(port, factory)
    if not plugin.relay:
        return p1, p2
    host = plugin.relay.get("host", "0.0.0.0")
    port = plugin.relay.get("port", None)
    if plugin.relay.get("disable-ssl", False):
        if port is None:
            port = 2587 if os.getuid() else 587
        p2 = reactor.listenTCP(int(port), factory, interface=host)
    else:
        if port is None:
            port = 2465 if os.getuid() else 465
        from phen.util.ssl import get_ctx
        p2 = reactor.listenSSL(int(port), factory, get_ctx(), interface=host)
    return p1, p2
