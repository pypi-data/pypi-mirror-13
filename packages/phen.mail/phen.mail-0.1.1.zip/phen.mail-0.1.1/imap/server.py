# -*- coding:utf-8 -*-

import logging
from twisted.mail import imap4
from twisted.cred import portal
from zope.interface import implementer
from twisted.internet import protocol

from .account import Account


log = logging.getLogger(__name__)


class IMAP4Debug(imap4.IMAP4Server):
    IDENT = 'Phen IMAP4rev1 Ready'

    def lineReceived(self, line):
        log.debug("<- " + line)
        imap4.IMAP4Server.lineReceived(self, line)

    def sendLine(self, line):
        imap4.IMAP4Server.sendLine(self, line)
        log.debug("-> " + line)

    # Geary requires something after the +
    def do_IDLE(self, tag):
        self.sendContinuationRequest("idling")
        self.parseTag = tag
        self.lastState = self.parseState
        self.parseState = 'idle'

    select_IDLE = (do_IDLE,)
    auth_IDLE = select_IDLE

    # Twisted does not deal with partial uploads, so we fix it here
    def spew_body(self, part, id, msg, _w=None, _f=None):
        if _w is None:
            _w = self.transport.write
        for p in part.part:
            if msg.isMultipart():
                msg = msg.getSubPart(p)
            elif p > 0:
                # Non-multipart messages have an implicit first part but no
                # other parts - reject any request for any other part.
                raise TypeError("Requested subpart of non-multipart message")

        if part.header:
            hdrs = msg.getHeaders(part.header.negate, *part.header.fields)
            hdrs = imap4._formatHeaders(hdrs)
            _w(str(part) + ' ' + imap4._literal(hdrs))
        elif part.text:
            _w(str(part) + ' ')
            _f()
            return imap4.FileProducer(
                msg.getBodyFile(part.partialBegin, part.partialLength)
            ).beginProducing(self.transport)
        elif part.mime:
            hdrs = imap4._formatHeaders(msg.getHeaders(True))
            _w(str(part) + ' ' + imap4._literal(hdrs))
        elif part.empty:
            _w(str(part) + ' ')
            _f()
            if part.part:
                return imap4.FileProducer(
                    msg.getBodyFile(part.partialBegin, part.partialLength)
                ).beginProducing(self.transport)
            else:
                mf = msg.as_file(part.partialBegin, part.partialLength)
                return imap4.FileProducer(mf).beginProducing(self.transport)
        else:
            _w('BODY ' + imap4.collapseNestedLists(
                [imap4.getBodyStructure(msg)]
            ))


class Factory(protocol.Factory):

    def buildProtocol(self, address):
        p = self.protocol()
        p.portal = self.portal
        p.factory = self
        return p


@implementer(portal.IRealm)
class Realm:
    avatarInterfaces = {imap4.IAccount: Account}

    def requestAvatar(self, avatar, mind, *ifaces):
        if imap4.IAccount in ifaces:
            account = Account(avatar.ctx, avatar.folder)
            return imap4.IAccount, account, lambda: None
        else:
            raise Exception("No supported interfaces found.")
