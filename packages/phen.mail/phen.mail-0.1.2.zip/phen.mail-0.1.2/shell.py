# -*- coding:utf-8 -*-

from phen.shell.base import ProtectedSubCmd, protected, shlexed, requires_cid
from phen.shell.util import input_passphrase, input_question


class Shell(ProtectedSubCmd):
    """
        Mail management.
    """
    cmdname = "mail"

    def __init__(self, parent, *p, **kw):
        from phen.plugin import Manager
        self.plugin = Manager.singleton["mail"].plugin
        ProtectedSubCmd.__init__(self, *p, **kw)
        self.parent = parent
        self.ctx = parent.ctx

    def preloop(self):
        self.update_prompt()

    def update_prompt(self):
        if self.color:
            pfmt = "\x1b[1;32mmail\x1b[0m$ "
        else:
            pfmt = "mail$ "
        self.prompt = pfmt

    @protected
    def do_reload(self, args):
        """reload

        Reload the configuration and restart the servers.

        """
        self.plugin.reload_servers()

    @protected
    def do_shutdown(self, args):
        """shutdown

        Shutdown the servers.

        """
        self.plugin.shutdown_servers()

    @protected
    def do_genDKIM(self, args):
        """genDKIM

        Generate a DKIM key for signing relayed emails.

        """
        from phen.context import device
        if not self.plugin._generate_dkim_key(device):
            ans = input_question(
                self,
                "Do you want to overwrite the current DKIM key? (y/N) "
            ).lower()
            if not ans or ans[0] != "y":
                return self.send("canceled")
            self.plugin._generate_dkim_key(device, True)
        return self.send("New DKIM key generated, happy mail signing!")

    @shlexed
    @requires_cid
    def do_passwd(self, args):
        """passwd [pop3]

        Change the pass-phrase of the mail folder (i.e., the folder
        currently selected). In case no configuration file exists,
        on will be created. If `pop3` is specified, the pass-phrase
        for the APOP authentication method is set.

        """
        if args:
            if args[0].lower() != "pop3":
                return self.do_help("passwd")
            pop = True
        else:
            pop = False
        passphrase = input_passphrase(self, "Type in the new pass-phrase: ")
        from phen.util import config
        cfg = config.load(self.ctx.fs, u"mail.jcfg", abscence_ok=True)
        if pop:
            from phen.util import obscure
            cfg["pop3pwd"] = obscure(passphrase)
        else:
            import hashlib
            cfg["passphrase"] = hashlib.sha256(passphrase).hexdigest()
        try:
            self.ctx.fs.json_write(u"mail.jcfg", cfg)
        except Exception as exc:
            self.send(exc)

    @shlexed
    @requires_cid
    def do_invalidate(self, args):
        """invalidate [<mailbox-path>]

        Force IMAP clients to reload the contents of the folder.

        """
        path = args[0] if args else self.ctx.fs.curdir
        if path.endswith("/cur"):
            path = path[:-4]
        try:
            xattr = self.ctx.fs.xattr(path)
            if "uid_validity" not in xattr:
                return self.send("The folder doesn't seem to be a mailbox")
            xattr["uid_validity"] += 1
            self.ctx.fs.xattr(path, xattr)
        except Exception as exc:
            self.send(exc)
