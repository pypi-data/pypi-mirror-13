# -*- coding:utf-8 -*-

import io
import logging
from twisted.mail import imap4, pop3
from twisted.internet import protocol, defer, endpoints, reactor

from phen.util import clarify

from .delivery import process
from .common import checker


log = logging.getLogger(__name__)


class Account:
    def __init__(self, fetcher, cfg):
        self.cfg = cfg
        self.fetcher = fetcher
        from phen.util import str_to_seconds
        self.period = str_to_seconds(self.cfg.get("period", 300))
        self.username = self.cfg["username"].encode("utf8")
        self.passphrase = clarify(self.cfg["passphrase"]).encode("utf8")
        self.boxes = self.cfg.get("boxes")
        if not self.boxes:
            self.boxes = ["Inbox"]
        self.build_endpoint()
        self.schedule(1)

    def schedule(self, secs=None):
        reactor.callFromThread(
            reactor.callLater, secs or self.period, self.fetch
        )

    def build_endpoint(self):
        proto = self.cfg.get("protocol", "imaps")
        proto = proto.replace("4", "").replace("3", "")
        port = dict(imap=143, imaps=993, pop=110, pops=995).get(proto)
        port = self.cfg.get("port", port)
        ep_spec = "{t}:host={h}:port={p}".format(
            t="ssl" if proto.endswith("s") else "tcp",
            h=self.cfg["server"], p=port,
        )
        self.acc_id = ep_spec + self.username
        self.endpoint = endpoints.clientFromString(reactor, ep_spec)
        self.factory = protocol.Factory()
        if proto.startswith("pop"):
            self.fetch = self.fetch_pop
            self.factory.protocol = pop3.POP3Client
        else:
            self.factory.protocol = imap4.IMAP4Client

    def iter_boxes(self):
        for box in self.boxes:
            if isinstance(box, dict):
                for k, v in box.items():
                    yield k, v.split(":")
            else:
                yield box, ["filter"]

    @defer.inlineCallbacks
    def fetch_imap(self):
        log.debug("fetching " + self.acc_id)
        try:
            client = yield self.endpoint.connect(self.factory)
            yield client.login(self.username, self.passphrase)
            for box, action in self.iter_boxes():
                last_uid = self.fetcher[self.acc_id + box]
                info = yield client.status(box, 'UIDNEXT')
                cur_uid = int(info['UIDNEXT'])
                if last_uid == cur_uid:
                    continue
                if last_uid is None:
                    if self.cfg.get("first-time") != 'download-all':
                        self.fetcher[self.acc_id + box] = cur_uid
                        continue
                    last_uid = 1
                yield client.select(box.encode("utf8"))
                msg_list = yield client.fetchUID(
                    imap4.MessageSet(last_uid, cur_uid), True
                )
                for msn in msg_list:
                    data = yield client.fetchMessage(imap4.MessageSet(msn))
                    self.fetcher.deliver(action, data[msn]["RFC822"])
                self.fetcher[self.acc_id + box] = cur_uid
            yield client.logout()
        except:
            log.exception("while fetching for " + self.acc_id)
        self.schedule()

    @defer.inlineCallbacks
    def fetch_pop(self):
        pass

    fetch = fetch_imap


class MailFetcher:
    @staticmethod
    def for_ctx(ctx):
        from phen.util import config
        path = ctx.cid.subpath("system/config/mail-fetcher.jcfg")
        cfg = config.load(ctx.fs, path, abscence_ok=True)
        mutex = cfg.get("device")
        if mutex and mutex != ctx.device.cidhash:
            return
        if "accounts" not in cfg:
            return
        return MailFetcher(ctx, cfg)

    def __init__(self, ctx, cfg):
        self.ctx = ctx
        self.accounts = [Account(self, acc_cfg) for acc_cfg in cfg["accounts"]]
        self.state_path = ctx.cid.subpath("system/config/mail-fetcher.state")
        folders = cfg.get("mail-folders")
        if not folders:
            folders = {"mail": ctx.cid.subpath("mail")}
        self.folders = {}
        for f in folders:
            avatar = checker.Avatar(ctx.cidhash)
            avatar.get_config(folders[f])
            self.folders[f] = process.Delivery(avatar)
        try:
            self.state = ctx.fs.json_read(self.state_path)
        except IOError:
            self.state = {}

    def __getitem__(self, key):
        return self.state.get(key)

    def __setitem__(self, key, value):
        self.state[key] = value
        self.ctx.fs.json_write(self.state_path, self.state)

    def deliver(self, action, msg):
        log.debug("delivering " + ":".join(action))
        msg_file = io.BytesIO(msg)
        if action[0] == "filter":
            if len(action) > 1:
                self.folders[action[1]].process(msg_file)
        elif action[0] == "accept":
            f, box = action[1:3] if len(action) > 2 else ("mail", action[1])
            self.folders[f].process(msg_file, box)
        else:
            log.warn("invalid action: " + ":".join(action))
