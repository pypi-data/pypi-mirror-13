# -*- coding:utf-8 -*-

import hashlib
from zope.interface import implementer
from twisted.mail.pop3 import APOPCredentials
from twisted.cred.error import UnauthorizedLogin
from twisted.cred.checkers import ICredentialsChecker
from twisted.cred.credentials import IUsernamePassword

from phen.util import path_join as pj


class Avatar(object):
    """Holds information about the peer"""

    def __init__(self, username=None):
        self.username = username
        self.external_MDA = False
        self.idhash = None
        self.folder = None
        from phen.context import device
        self.ctx = None if username else device
        self.cfg = {}

    @property
    def is_anonynous(self):
        return not self.username

    def get_config(self, folder):
        from phen.context import Context, device
        self.folder = folder
        self.idhash = folder[1:44]
        self.ctx = Context.get_service_context(self.idhash) or device
        from phen.util import config
        self.cfg = config.load(self.ctx.fs, pj(folder, "mail.jcfg"))
        self.external_MDA = self.cfg.get("external-MDA", False)

    def check(self, cred_pass, folder):
        self.get_config(folder)
        if not self.cfg or self.cfg.get("passphrase") != cred_pass:
            raise UnauthorizedLogin("Unauthorized user")
        return self

    def check_apop(self, cred, folder):
        from phen.util import clarify
        self.get_config(folder)
        pwd = self.cfg and self.cfg.get("pop3pwd")
        if not pwd or not cred.checkPassword(clarify(pwd)):
            raise UnauthorizedLogin("Unauthorized user")
        return self


@implementer(ICredentialsChecker)
class Checker:
    credentialInterfaces = (IUsernamePassword,)

    def __init__(self, plugin, allow_external_MDA=False):
        self.plugin = plugin
        self.allow_external_MDA = allow_external_MDA

    def requestAvatarId(self, credentials):
        folder = self.plugin.get_user_folder(credentials.username)
        if folder is None:
            raise UnauthorizedLogin("Unauthorized user")
        retv = Avatar(credentials.username)
        if isinstance(credentials, APOPCredentials):
            if folder[0] != "/":
                raise UnauthorizedLogin("Unauthorized user")
            return retv.check_apop(credentials, folder)
        cred_pass = hashlib.sha256(credentials.password).hexdigest()
        if folder[0] == ">":
            passphrase = folder.split()[-1]
            if not self.allow_external_MDA or passphrase != cred_pass:
                raise UnauthorizedLogin("Unauthorized user")
            retv.external_MDA = folder
            return retv
        return retv.check(cred_pass, folder)
