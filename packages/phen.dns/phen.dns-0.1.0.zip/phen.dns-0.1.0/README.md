DNS Plugin for Phen
===================

Simple DNS server for sites based on Phen, or for keeping track of
computers with dynamic IP addresses. Other plugins can use the
internal extension mechanism to add records, e.g. the mail plugin
can add MX and SPF records.

Example configuration file:
```
{
  "verbose": false,     # log requests (default false)
  "http-path": "dns",   # for IP update through http(s) request
                        # (requires the http plugin to be loaded)
  "recursive": false,   # for non-authoritative servers (default false)
  "zones": {
    "phen.eu": [
      {
        "mname": "ns1.phen.eu",
        "rname": "contact.phen.eu",
        "serial": 201512150,
        "refresh": "20m",
        "retry": "5m",
        "expire": "14d",
        "minimum": "5m"
      },
      {"type": "NS", "name": "ns1.phen.eu"},
      {"subdomain": "ns1", "type": "A", "address": "78.47.100.138"},
      {"subdomain": "ns2", "type": "A", "address": "78.47.100.138"},
      {"type": "A", "address": "78.47.100.138"},
      {"type": "AAAA", "address": "2a01:4f8:c17:1bff::2"},
      {"subdomain": "www", "type": "A", "address": "78.47.100.138"},
      {"subdomain": "opo",
       "type": "CNAME", "name": "some.dyndns.moo", "ttl": 300},
      {"subdomain": "cxs",
       "type": "A", "dynamic": "some identity fingerprint", "ttl": 300},
       {"subdomain": "poa",
        "type": "A", "dynamic": ">sha256(my-secret-password)", "ttl": 300}
    ]
  }
}
```

To update a dynamic dns entry:
```
wget "https://phen.eu/dns?pwd=my-secret-password&domain=poa.phen.eu&ip=4.3.2.1"
```
