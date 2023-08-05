# -*- coding:utf-8 -*-

from phen.shell.base import ProtectedSubCmd, protected, shlexed


class Shell(ProtectedSubCmd):
    """
        DNS shell.
    """
    cmdname = "dns"

    def __init__(self, parent, *p, **kw):
        ProtectedSubCmd.__init__(self, *p, **kw)
        self.parent = parent
        from phen.plugin import Manager
        self.server = Manager.singleton["dns"].plugin.server
        self.ctx = parent.ctx
        self.chn = None

    def preloop(self):
        self.update_prompt()

    def update_prompt(self):
        if self.color:
            pfmt = "\x1b[1;32mdns\x1b[0m$ "
        else:
            pfmt = "dns$ "
        self.prompt = pfmt

    @shlexed
    @protected
    def do_reload(self, args):
        """reload

        Apply any configuration changes.

        """
        try:
            if args:
                return self.do_help("reload")
            self.server.reload()
            self.send("Configuration reloaded")
        except Exception as e:
            self.send(e)

    @shlexed
    @protected
    def do_list(self, args):
        """list

        List the dynamic entries.

        """
        try:
            if args:
                return self.do_help("list")
            from .dns import DynamicAddress
            DynamicAddress._load_state()
            for name in DynamicAddress.registry:
                self.send("{}: {} ({})".format(
                    name, DynamicAddress.state.get(name, "---"),
                    DynamicAddress.registry[name].idhash
                ))
        except Exception as e:
            self.send(e)
