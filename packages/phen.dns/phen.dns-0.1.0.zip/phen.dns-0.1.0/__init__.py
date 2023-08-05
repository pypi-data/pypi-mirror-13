# -*- coding:utf-8 -*-


class Plugin:
    def __init__(self, manager):
        from .dns import Server
        self.manager = manager
        self.server = Server()
        self.http_plugin = None

    def complement_shell(self, wrapper):
        from .shell import Shell
        wrapper.plugin.attach(Shell)

    def complement_http(self, wrapper):
        self.http_plugin = wrapper.plugin

    def device_loaded(self):
        self.server.setup(self.http_plugin)

    def shutdown(self):
        self.server.shutdown()
