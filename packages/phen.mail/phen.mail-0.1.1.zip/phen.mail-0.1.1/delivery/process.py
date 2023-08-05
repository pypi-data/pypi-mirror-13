# -*- coding:utf-8 -*-

import logging
from phen.util import hex_suffix, path_join as pj
from .filters import AcceptMail, RejectMail, Filter


log = logging.getLogger(__name__)
global_filters = []


class Delivery:
    def __init__(self, avatar):
        self.avatar = avatar
        self.delivery_folder = self.avatar.cfg.get("delivery")
        if not self.delivery_folder:
            self.delivery_folder = pj(self.avatar.folder, u"delivery")
        self._load_filters()

    def _load_filters(self):
        from phen.util import config
        try:
            filter_file = self.avatar.cfg.get("filters")
            if not filter_file:
                filter_file = pj(self.avatar.folder, u"filters.jcfg")
            if self.avatar.ctx.fs.exists(filter_file):
                cfg = config.load(self.avatar.ctx.fs, filter_file)
            else:
                cfg = {}
            self.filters = [
                Filter(**f) for f in cfg.get("filters", [])
            ]
            if self.avatar.cfg.get("use-global-filters"):
                self.filters += global_filters
        except IOError:
            from traceback import print_exc
            print_exc()
            self.filters = []

    def apply_filters(self, message, simulation=None):
        action = None
        for filter in self.filters:
            try:
                filter.analyze(self.avatar, self.avatar.ctx, message)
            except AcceptMail as action:
                break
            except RejectMail as action:
                if simulation is not None:
                    simulation("reject", action.args[0], message)
                return None
            except Exception as exc:
                from traceback import print_exc
                print_exc()
                if simulation is not None:
                    simulation("exception", exc.args[0], message)
                continue
        box_path = "Inbox" if action is None else action.args[0]
        if simulation is not None:
            simulation("accept", box_path, message)
        return box_path

    def process(self, msg_file, box_path=None):
        if self.avatar.ctx.device == self.avatar.ctx:
            # should check if the mailboxes are writeable by the device
            # but for now let's just deliver to the default folder
            path = pj(
                self.avatar.folder, self.delivery_folder, hex_suffix("mail")
            )
            try:
                with self.avatar.ctx.fs.open(path, 'wd') as out:
                    out.write(msg_file.read())
            except IOError:
                # todo: bounce
                pass
            return
        import email
        msg = email.message_from_file(msg_file)
        if not box_path:
            box_path = self.apply_filters(msg)
        if box_path:
            log.debug("deliver to " + box_path)
            parts = ["." + p for p in box_path.split("/")]
            from ..common.mailbox import MailBox
            path = pj(self.avatar.folder, *parts)
            if not self.avatar.ctx.fs.exists(path):
                self.avatar.ctx.fs.makedirs(path)
            box = MailBox(self.avatar.ctx, path)
            msg_file.seek(0)
            box.add(msg_file)
        else:
            log.debug("mail discarded")
