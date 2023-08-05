# -*- coding:utf-8 -*-

import time
import email
import logging
import email.utils
from twisted.mail import smtp, relaymanager
from twisted.internet import defer, protocol, reactor

from phen import plugin
from phen.util import hex_suffix, path_join as pj
from ..delivery import message


log = logging.getLogger(__name__)


def bounce_message(reason, from_addr, msg):
    cfg = plugin.Manager.singleton["mail"].plugin.config.get("bounce", {})
    subject = cfg.get("subject", "mail delivery error")
    warning = cfg.get(
        "warning",
        "The mail you've sent could not be delivered: {reason}\n\n"
        "Mail headers follow:\n{headers}"
    )
    if not hasattr(msg, "as_string"):
        msg = email.message_from_file(msg)
    retv = email.message.Message()
    retv["From"] = from_addr
    retv["To"] = msg["From"]
    retv["Date"] = email.utils.formatdate(time.time())
    retv["Subject"] = subject
    msg.set_payload("")
    retv.set_payload(warning.format(reason=reason, headers=msg.as_string()))
    return retv


class Message(message.Base):
    def __init__(self, origin, dest):
        message.Base.__init__(self)
        self.plugin = plugin.Manager.singleton["mail"].plugin
        self.domain = self.plugin.sender_domain
        self.manager = self.plugin.relay_manager
        self.origin = origin
        self.dest = dest
        if self.domain != origin.domain:
            self.senderID = "@".join((origin.local, self.domain))
        else:
            self.senderID = None

    def eomReceived(self):
        raw = self.buffer.getvalue()
        self.buffer = None
        msg = email.message_from_string(raw)
        if self.plugin.config.get("hosted"):
            self.msg = msg
            self.plugin.send_mail(
                None, self.dest, msg
            ).addErrback(self._hosted_bounce)
        else:
            del msg["DKIM-Signature"]
            if self.senderID:
                msg["Sender"] = self.senderID
            if self.manager.dkim_key:
                from dkim import sign
                msg["DKIM-Signature"] = sign(
                    raw, "all", self.domain, self.manager.dkim_key
                )[16:]
            self.manager.add(self.origin, self.dest, msg)
        return defer.succeed(None)

    def _hosted_bounce(self, reason):
        if self.origin.local == "postmaster":
            return
        from_addr = "postmaster@" + self.domain
        self.plugin.send_mail(
            from_addr, str(self.origin),
            bounce_message(reason, from_addr, self.msg)
        ).addErrback(lambda x: None)


class ESMTPRelayer(smtp.ESMTPClient):
    def __init__(self, queue, *args):
        smtp.ESMTPClient.__init__(self, *args)
        self.queue = iter(queue)

    def getMailFrom(self):
        try:
            self.item = next(self.queue)
        except StopIteration:
            return
        return self.item.from_addr

    def getMailTo(self):
        log.debug("relay mailto: %r" % self.item.to_addr)
        return [self.item.to_addr]

    def getMailData(self):
        if hasattr(self.item.msg, "as_string"):
            import io
            return io.BytesIO(self.item.msg.as_string())
        return self.item.msg

    def sentMail(self, code, resp, numOk, addresses, log_res):
        log.debug("relay result: %r %r" % (code, resp))
        if code in smtp.SUCCESS:
            self.item.success()
        self.item.fail(code, resp)


class RelayerFactory(protocol.ClientFactory):
    protocol = ESMTPRelayer
    sslctx = None

    def __init__(self, queue, identity):
        self.queue = queue
        self.identity = identity.encode("latin1")

    def buildProtocol(self, address):
        if not self.sslctx:
            from phen.util.ssl import get_ctx
            RelayerFactory.sslctx = get_ctx()
        p = self.protocol(self.queue, None, self.sslctx, self.identity)
        p.factory = self
        return p

    def clientConnectionFailed(self, connector, reason):
        self.queue.connection_failed()


class QueueItem(object):
    max_tries = 5

    def __init__(self, queue, from_addr, to_addr, msg, **kw):
        self.queue = queue
        self.from_addr = from_addr
        self.to_addr = to_addr
        self._msg = msg
        self.next_try = kw.get("next_try", 0)
        self.tries = kw.get("tries", 0)
        self.path = kw.get("path")
        self.fails = kw.get("fails", [])

    @property
    def msg(self):
        if not self._msg:
            self._msg = self.queue.manager.open_message(self.path)
        if hasattr(self._msg, "seek"):
            self._msg.seek(0)
        return self._msg

    @property
    def can_send(self):
        return not self.next_try or self.next_try <= time.time()

    def hibernate(self):
        self.queue.manager.hibernate_item(self)

    def success(self):
        self.queue.remove(self)

    def fail(self, code, response):
        try:
            code = int(code)
        except ValueError:
            response += " (original code: %r)" % code
            code = 666
        if int(code) == 250:
            return self.success()
        log.debug("relaying to {} ({}) failed - {}:{}".format(
            self.queue.address, self.to_addr, code, response
        ))
        if code > 500:
            self.queue.manager.bounce(self.from_addr, response, self.msg)
            return self.queue.remove(self)
        self.fails.append((code, response))
        self.tries += 1
        if self.tries == self.max_tries:
            self.queue.manager.bounce(
                self.from_addr,
                "\n".join(str(f) for f in self.fails),
                self.msg
            )
            return self.queue.remove(self)
        self.next_try = time.time() + 60 * 2 ** (self.tries - 1)


class DomainQueue:
    mxcalc = None
    max_tries = 7
    warn_try_number = 3
    wait_interval = 60      # to avoid hammering servers and getting banned.
    retry_interval = 3     # period to wait if the server wasn't reacheable.

    def __init__(self, manager, name):
        self.manager = manager
        self.name = name
        self.not_before = 0
        self.queue = []
        self.address = None
        self.ttd = 0
        self.tries = 0
        self.processing = False

    def shutdown(self):
        for item in self.queue:
            item.hibernate()

    def check(self):
        if self.processing or self.not_before > time.time():
            return True
        if not self.queue:
            self.manager.domain_done(self.name)
            return False
        if not any(item.can_send for item in self.queue):
            return True
        self.processing = True
        self.resolve()
        return True

    def add(self, from_addr, to_addr, msg=None, **kw):
        item = QueueItem(self, from_addr, to_addr, msg, **kw)
        self.queue.append(item)

    def remove(self, item):
        if item in self.queue:
            self.queue.remove(item)
        if item.path:
            self.manager.remove_message(item.path)

    def __iter__(self):
        keep_checking = True
        while keep_checking:
            keep_checking = False
            for item in self.queue[:]:
                if item.can_send:
                    keep_checking = True
                    yield item
        self.batch_finished()

    def bounce_all(self, reason, emptyQueue=True):
        for item in self.queue:
            self.manager.bounce(item.from_addr, reason, item.msg)
        if emptyQueue:
            while self.queue:
                self.remove(self.queue[0])
        self.processing = False

    def resolve(self):
        if time.time() < self.ttd:
            return self.resolved()
        if self.mxcalc is None:
            DomainQueue.mxcalc = relaymanager.MXCalculator()
        d = self.mxcalc.getMX(self.name)
        d.addCallback(self._mx_resolved)
        d.addErrback(self._mx_unresolvable)

    def _mx_resolved(self, mx):
        self.address = str(mx.name)
        self.ttd = (mx.ttl or 10 ** 5) + time.time()
        self.resolved()

    def _mx_unresolvable(self, reason):
        log.debug("error 512 - {}".format(reason.getErrorMessage()))
        self.bounce_all(reason.getErrorMessage())

    def resolved(self):
        reactor.connectTCP(
            self.address, 25, RelayerFactory(self, self.manager.domain)
        )

    def batch_finished(self):
        self.tries = 0
        self.not_before = time.time() + self.wait_interval
        self.processing = False
        if self.queue:
            reactor.callLater(self.wait_interval, self.check)

    def connection_failed(self):
        log.debug("connection to {} failed (error 101)".format(self.address))
        self.tries += 1
        self.processing = False
        if self.tries == self.warn_try_number:
            self.bounce_all(
                "{} unsuccessful connection attempts (I'll stop at {})"
                .format(self.tries, self.max_tries),
                False
            )
        elif self.tries == self.max_tries:
            self.bounce_all("giving up after {} attempts" .format(self.tries))
            self.tries = 0
            return self.manager.domain_done(self.name)
        mult = 2 ** (self.tries - 1)
        self.not_before = time.time() + self.retry_interval * mult


class Manager:
    def __init__(self, plugin, ctx, cfg):
        self.plugin = plugin
        self.domain = plugin.sender_domain
        self.ctx = ctx
        self.cfg = cfg
        self.dkim_key = None
        self.domains = {}
        self.folder = self.cfg.get("queue-folder", None)
        if not self.folder:
            self.folder = self.ctx.cid.subpath(u"system/mail/queue")
        self.exists = self.ctx.fs.exists(self.folder)
        self.startup()

    def send_mail(self, from_addr, to_addrs, msg):
        origin = smtp.Address(from_addr)
        if hasattr(msg, "as_string"):
            msg = msg.as_string()
        if origin.domain in self.plugin.config.get("domains", []):
            from ..common.checker import Avatar
            folder = self.plugin.get_user_folder(from_addr)
            if not folder:
                return self.bounce(from_addr, "user does not exist", msg)
            avatar = Avatar()
            avatar.get_config(folder)
            import io
            from ..delivery.process import Delivery
            delivery = Delivery(avatar)
            delivery.process(io.BytesIO(msg))
            return
        sign_msg = Message(origin, to_addrs)
        sign_msg.buffer.write(msg)
        sign_msg.eomReceived()

    def bounce(self, origin, reason, msg):
        if str(origin).startswith("postmaster@"):
            return
        from_addr = "postmaster@" + self.domain
        self.send_mail(
            from_addr, str(origin), bounce_message(reason, from_addr, msg)
        )

    def _queue_for_dest(self, dest):
        name, addr = email.utils.parseaddr(dest)
        user, domain = addr.split('@', 1)
        queue = self.domains.get(domain)
        if not queue:
            queue = self.domains[domain] = DomainQueue(self, domain)
        return queue

    def add(self, from_addr, to_addrs, msg):
        if not isinstance(to_addrs, list):
            to_addrs = [to_addrs]
        for to_addr in to_addrs:
            self._queue_for_dest(to_addr).add(
                str(from_addr), str(to_addr), msg
            )
        reactor.callLater(1, self.check)

    def domain_done(self, name):
        self.domains.pop(name)

    def check(self):
        check_again = False
        for domain, queue in list(self.domains.items()):
            check_again |= queue.check()
        if check_again:
            reactor.callLater(60, self.check)

    def open_message(self, path):
        return self.ctx.fs.open(path, "r")

    def remove_message(self, path):
        self.ctx.fs.unlink(path)
        self.ctx.fs.unlink(path + ".meta")

    def hibernate_item(self, item):
        if not self.exists:
            self.ctx.fs.mkdir(self.folder)
        if not item.path:
            item.path = pj(self.folder, hex_suffix(u""))
            with self.ctx.fs.open(item.path, "wd") as out:
                if hasattr(item.msg, "as_string"):
                    out.write(item.msg.as_string())
                else:
                    out.write(item.msg)
        self.ctx.fs.json_write(item.path + ".meta", {
            k: getattr(item, k)
            for k in "from_addr to_addr tries next_try fails".split()
        })

    def startup(self):
        if not self.exists:
            return
        for name in self.ctx.fs.listdir(self.folder):
            if not name.endswith(".meta"):
                continue
            path = pj(self.folder, name)
            meta = self.ctx.fs.json_read(path)
            queue = self._queue_for_dest(meta.get("to_addr"))
            import six
            if six.PY2:
                for attr in ("from_addr", "to_addr"):
                    meta[attr] = meta[attr].encode("latin1")
            meta["path"] = path[:-5]
            queue.add(**meta)
        if self.domains:
            # this method is not called from the reactor thread
            reactor.callFromThread(reactor.callLater, 1, self.check)

    def shutdown(self):
        for queue in self.domains.values():
            queue.shutdown()
