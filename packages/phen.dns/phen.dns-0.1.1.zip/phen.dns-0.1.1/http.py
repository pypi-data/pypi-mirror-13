# -*- coding:utf-8 -*-

from twisted.web import resource


tpl = "Phen Dynamic DNS: %s\n"


class Updater(resource.Resource):
    def render_GET(self, request):
        try:
            ip = request.args.get("ip", [request.getClientIP()])[0]
        except:
            return tpl % "incorrect IP address"
        try:
            pwd = request.args.get("pwd", [None])[0]
        except:
            pwd = None
        if not pwd:
            return tpl % "couldn't retrieve the password from the request"
        try:
            domain = request.args.get("domain", [None])[0]
        except:
            domain = None
        if not domain:
            return tpl % "couldn't retrieve the domain from the request"
        from .dns import DynamicAddress
        if domain not in DynamicAddress.registry:
            return tpl % ("domain '%s' is not valid" % domain)
        try:
            updated = DynamicAddress.registry[domain].update(ip, pwd)
        except:
            updated = False
        return tpl % ("success" if updated else "update not accepted")
