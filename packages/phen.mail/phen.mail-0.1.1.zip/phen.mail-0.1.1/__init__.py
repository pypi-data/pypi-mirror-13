# -*- coding:utf-8 -*-

import socket
import logging

log = logging.getLogger(__name__)


class Plugin:
    def __init__(self, manager):
        self.manager = manager
        self.config = {}
        self.sender_domain = None
        self.relay_manager = None
        self.spf = None
        self.dns_dkim_key = None
        self.imap = self.pop3 = None
        self.smtp = ()

    # -=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=:[ interaction with other plugins

    def complement_dns(self, wrapper):
        dns_server = wrapper.plugin.server
        dns_server.loading_config.subscribe(self._add_dns_entries)

    def complement_shell(self, wrapper):
        from .shell import Shell
        wrapper.plugin.attach(Shell)

    complement_ssh = complement_shell

    def mail_received(self, msg, origin, param):
        # self interaction :)
        msg["Subject"] = "Re: " + msg["Subject"]
        payload = msg.get_payload(decode=True)
        payload = "Mailed to the 'mail' plugin{}\n\nParameters: {}".format(
            (":\n" + payload) if payload else ".", param
        )
        msg.set_payload(payload)
        self.sendmail(None, msg["From"], msg)

    def send_mail(self, from_addr, to_addrs, msg):
        from phen.util import clarify
        from twisted.mail.smtp import sendmail
        host = self.config.get("hosted")
        if host:
            return sendmail(
                host.get("server"),
                from_addr or host.get("username"), to_addrs, msg,
                port=host.get("port", 465),
                username=host.get("username"),
                password=clarify(host.get("password")),
                requireAuthentication=host.get("require-authentication", True),
                requireTransportSecurity=host.get("require-tls", True),
            )
        if self.relay_manager:
            self.relay_manager.send_mail(from_addr, to_addrs, msg)

    # -=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-

    def shutdown(self):
        """Plugin shutdown"""
        self.shutdown_servers()
        if self.relay_manager:
            self.relay_manager.shutdown()
            self.relay_manager = None

    def startup_servers(self):
        from phen.context import Context
        Context.created.subscribe(self.context_created)
        self._load_config()
        from . import imap, smtp, pop3
        for mod in (imap, smtp, pop3):
            name = mod.__name__.split(".")[-1]
            cfg = self.config.get(name)
            if isinstance(cfg, bool):
                cfg = {"disabled": not cfg}
            if cfg and not cfg.get("disabled", False):
                setattr(self, name, mod.setup(self, cfg))

    def device_loaded(self):
        self.startup_servers()
        from phen.context import Context
        Context.call_with_sctx(self.identity_loaded)

    def shutdown_servers(self):
        for port in self.smtp + (self.imap, self.pop3):
            if port:
                # todo: check why this isn't working
                port.stopListening()
        self.smtp = ()
        self.imap = self.pop3 = None

    def reload_servers(self):
        self.shutdown_servers()
        self.startup_servers()

    def _add_dns_entries(self, dns_server):
        entries = []
        for recv in self.config.get("receivers", []):
            entries.append(dict(type="MX", preference=recv[0], name=recv[1]))
        if self.sender_domain is not None:
            if self.spf is not None:
                entries += [
                    {"type": "SPF", "data": [self.spf]},
                    {"type": "TXT", "data": [self.spf]},
                ]
            if self.dns_dkim_key is not None:
                entries.append(
                    {"subdomain": "all._domainkey", "type": "TXT",
                     "data": self.dns_dkim_key}
                )
        if entries:
            dns_server.add_entries(self.sender_domain, entries)

    def _load_config(self):
        from phen.util import config
        from phen.context import device
        path = device.cid.subpath("system", "mail")
        cfgfile = "/".join((path, "mail.jcfg"))
        if not device.fs.exists(path):
            device.fs.makedirs(path)
            device.fs.json_write(cfgfile, {})
        self.config = config.load(device.fs, cfgfile)
        self.sender_domain = self.config.get("sender-domain", socket.getfqdn())
        self.domains = self.config.get("domains", {})
        if not self.domains:
            return
        self.relay = self.config.get("relay", True)
        if isinstance(self.relay, bool):
            self.relay = {"disabled": not self.relay}
        if not self.relay.get("disabled"):
            self._setup_relay(device)
        else:
            self.relay_manager = None

    def _setup_relay(self, device):
        from .smtp import relay
        if not self.relay_manager:
            self.relay_manager = relay.Manager(self, device, self.relay)
        self.spf = " ".join(
            ["v=spf1 a ptr"] +
            ["include:" + d for d in self.domains
             if d != self.sender_domain] + ["-all"]
        ).encode("latin1")
        try:
            import dkim  # noqa
        except ImportError:
            log.warn("DKIM Python module missing, please install it")
            return
        dkim_key_path = self.relay.get("dkim-key")
        if dkim_key_path is None:
            dkim_key_path = device.cid.subpath("system/mail/dkim.key")
        try:
            self._load_dkim_key(device, dkim_key_path)
        except IOError:
            log.warn("couldn't load DKIM key " + dkim_key_path)

    def _generate_dkim_key(self, device, force=False):
        dkim_key_path = self.relay.get("dkim-key")
        if dkim_key_path is None:
            dkim_key_path = device.cid.subpath("system/mail/dkim.key")
        if device.fs.exists(dkim_key_path) and not force:
            return False
        from Crypto.PublicKey import RSA
        key = RSA.generate(1024)
        self.relay_manager.dkim_key = key.exportKey()
        with device.fs.open(dkim_key_path, "wd") as out:
            out.write(self.relay_manager.dkim_key)
        return True

    def _load_dkim_key(self, device, path):
        with device.fs.open(path, "rd") as in_:
            self.relay_manager.dkim_key = in_.read()
        from base64 import b64encode as b64e
        from Crypto.PublicKey import RSA
        key = RSA.importKey(self.relay_manager.dkim_key)
        text = "k=rsa; p=" + b64e(key.publickey().exportKey('DER')).rstrip("=")
        splice = 180
        self.dns_dkim_key = [
            text[i:i + splice]
            for i in range(0, len(text), splice)
        ]

    def get_user_folder(self, address, level=0):
        """Get the mail folder of a user, resolving alias recursively"""
        if not self.domains or level > 10:
            return None
        try:
            user, domain = address.split("@", 1)
        except ValueError:
            user, domain = address, self.sender_domain
        users = self.domains.get(domain)
        if not users:
            return None
        dest = users.get(user)
        if not dest or dest[0] not in ":/>.":
            return None
        if dest[0] in "/>.":
            return dest
        # :user[@otherdomain]
        if "@" in dest:
            return self.get_user_folder(dest[1:], level + 1)
        return self.get_user_folder("@".join((dest[1:], domain)), level + 1)

    def context_created(self, ctx):
        if not ctx.is_service_ctx:
            ctx.identity_loaded.subscribe(self.identity_loaded)

    def identity_loaded(self, ctx):
        sctx = ctx.get_service_context(ctx.cidhash)
        if not hasattr(sctx, "mail_fetcher"):
            from .fetcher import MailFetcher
            sctx.mail_fetcher = MailFetcher.for_ctx(sctx)
            if sctx.mail_fetcher:
                log.info("mail fetcher installed for %r" % ctx.cid)
