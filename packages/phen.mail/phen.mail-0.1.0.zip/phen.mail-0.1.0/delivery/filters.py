# -*- coding:utf-8 -*-


class AcceptMail(Exception):
    """Raised by a filter when accepting an email"""


class RejectMail(Exception):
    """Raised by a filter when rejecting an email"""


def accept(action):
    raise AcceptMail(action)


def reject(reason):
    raise RejectMail(reason)


class Filter:
    def __init__(self, **kw):
        self.__dict__.update(kw)
        self.error_log = None
        self._verified = False

    def _string_match(self, message):
        header = getattr(self, "header", "Subject")
        if header not in message:
            return
        header = message[header]
        mode = getattr(self, "mode", "contains")
        if mode == "contains":
            return self.content in header
        elif mode == "startswith":
            return header.startswith(self.content)
        elif mode == "endswith":
            return header.endswith(self.content)
        return False

    def _execute_script(self, avatar, **scope):
        ctx = scope["ctx"]
        if self.code.startswith("file:"):
            path = self.code[5:]
            if not path.startswith("/"):
                from phen.util import path_join as pj
                path = pj(avatar.folder, path)
            with ctx.fs.open(path) as src:
                code = src.read()
        else:
            code = self.code
        if not self._verified and ctx.account != 'admin':
            from phen.context import device
            user_cmd = avatar.idhash + code
            if not device.cid.verify(user_cmd, self.authorization):
                self.error_log = "script not authorized, please ask the admin"
                return  # let other filters analyze the message
        try:
            exec code in scope
        except StandardError:
            from traceback import format_exc
            self.error_log = format_exc()

    def analyze(self, avatar, ctx, message):
        if self.type == "match":
            if not self._string_match(message):
                return
            if self.action.startswith("accept"):
                accept(self.action[7:].strip())
            if self.action == "reject":
                reject(self.name)
        elif self.type == "py":
            self._execute_script(
                avatar, ctx=ctx, msg=message,
                accept=accept, reject=reject
            )
