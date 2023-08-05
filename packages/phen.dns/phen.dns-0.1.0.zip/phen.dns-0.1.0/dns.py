# -*- coding:utf-8 -*-

import os
import six
import time
from twisted.internet import reactor
from twisted.names import dns, server, client, authority, common

import logging

log = logging.getLogger(__file__)


# trick to avoid not responding anything to CAA record queries
common.typeToMethod[257] = 'lookupNull'


class DynamicAddress:
    expire = 60
    registry = {}

    def __init__(self, name, record, idhash):
        DynamicAddress.registry[name] = self
        self.record = record
        self.idhash = idhash
        self.manual = idhash.startswith(">")
        self.timestamp = 0

    def update(self, ip, passphrase=None):
        if passphrase is not None:
            from hashlib import sha256
            if sha256(passphrase).hexdigest() != self.idhash[1:]:
                return False
        import socket
        self.record.address = socket.inet_aton(ip)
        return True

    def check_address(self):
        if self.manual or time.time() - self.timestamp < self.expire:
            return
        self.timestamp = time.time()
        from phen.context import device
        from phen.p2pnet.connection import ConnectionMethod
        methods = ConnectionMethod.from_device(device, self.idhash)
        for method in methods:
            if method.host and method.host.split(".")[0] not in ("192", "10"):
                return self.update(method.host)


def encode_record(rec):
    if six.PY3:
        return
    for k in rec:
        if isinstance(rec[k], unicode):
            rec[k] = rec[k].encode("latin1")
    return rec


class Authority(authority.FileAuthority):
    calc_reverse = False

    def loadFile(self, zone_tuple):
        zone, records = zone_tuple
        self.records = {}
        self.dynamic = {}
        reverse = []
        for rec in records:
            rec = encode_record(rec.copy())
            rtype = rec.pop("type", "SOA")
            cls = getattr(dns, "Record_" + rtype)
            name = rec.pop("subdomain", None)
            name = zone if not name else ".".join((name, zone))
            idhash = rec.pop("dynamic", None)
            p = rec.pop("data", [])
            rinst = cls(*p, **rec)
            if idhash is not None:
                # we're assuming only A records may be dynamic
                self.dynamic[name.lower()] = DynamicAddress(
                    name.lower(), rinst, idhash
                )
            if rtype == "SOA":
                if rinst.serial < 0:
                    rinst.serial = int(time.strftime('%Y%m%d0'))
                self.soa = zone, rinst
            elif rtype == "A" and idhash is None:
                reverse.append((name, rec.get("address")))
            self.records.setdefault(name, []).append(rinst)
        # this might never be necessary, but whatever
        if self.calc_reverse:
            reverse.sort(key=lambda o: len(o[0]))
            name, address = reverse[0]
            rev_addr = ".".join(address.split(".")[::-1]) + ".in-addr.arpa"
            self.records[rev_addr] = [dns.Record_PTR(name)]

    def _lookup(self, name, cls, type, timeout=None):
        dynamic = self.dynamic.get(name.lower())
        if dynamic is not None and not dynamic.manual:
            dynamic.check_address()
        return authority.FileAuthority._lookup(self, name, cls, type, timeout)


class Server:
    def __init__(self):
        from phen.event import Event
        self.loading_config = Event()
        self.listeners = []
        self.factory = None
        self.http_plugin = None

    def setup(self, http_plugin):
        self.http_plugin = http_plugin
        self.http_installed = None
        self._load_config()
        verbose = self.cfg.get("verbose", 0)
        self.factory = server.DNSServerFactory(verbose=verbose)
        self._setup_resolvers()
        # interfaces = ["::", "0.0.0.0"]
        interfaces = [""]  # linux listens to both ipv4&6 by default
        port = None
        if port is None:
            port = 1053 if os.getuid() else 53
        for iface in interfaces:
            protocol = dns.DNSDatagramProtocol(self.factory)
            self.listeners.append(
                reactor.listenTCP(port, self.factory, interface=iface)
            )
            self.listeners.append(
                reactor.listenUDP(port, protocol, interface=iface)
            )

    def reload(self):
        self._load_config()
        self._setup_resolvers()

    def _load_config(self):
        from phen.context import device
        from phen.util import config
        path = device.cid.subpath("system/dns.jcfg")
        if not device.fs.exists(path):
            device.fs.json_write(path, {})
        self.cfg = config.load(device.fs, path)
        if self.http_plugin:
            self.install_http()

    def install_http(self):
        hpath = self.cfg.get("http-path")
        if self.http_installed and self.http_installed != hpath:
            self.http_plugin.server.root.delEntity(self.http_installed)
        self.http_installed = hpath
        from .http import Updater
        self.http_plugin.server.root.putChild(hpath, Updater())

    def add_entries(self, zone, entries):
        self.programatic.setdefault(zone, []).extend(entries)

    def _setup_resolvers(self):
        zones = self.cfg.get("zones", {})
        self.programatic = {}
        self.loading_config(self)  # call interested plugins, e.g. mail
        for zone in self.programatic:
            zones.setdefault(zone, []).extend(self.programatic[zone])
        try:
            resolvers = [Authority((zone, zones[zone])) for zone in zones]
        except Exception:
            log.exception("Error in DNS configuration, ignored")
            resolvers = []
        if self.cfg.get("recursive"):
            resolvers.append(client.Resolver(resolv='/etc/resolv.conf'))
        self.factory.resolver.resolvers = resolvers

    def shutdown(self):
        for handler in self.listeners:
            handler.stopListening()
