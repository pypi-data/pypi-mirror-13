#! /usr/bin/env python
# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from glb.settings import Config


def parse(data, protocol_support):
    if not data:
        data = list()
    upstreams = list()
    servers = list()
    ssl_files = set()
    for balancer in data:
        def __default_name():
            names = balancer.name.split("_")
            if len(names) > 2:
                names = names[:-1]
            names.append(Config.GLB_URL)
            return '.'.join(names)
        default_name = __default_name()
        upstream_name = '%s_upstream' % default_name
        protocol = balancer.frontend['protocol']
        backends = getattr(balancer, 'backends', [])

        def parse_upstream():
            servs = ["%s:%s" % (backend['address'], backend['port'])
                     for backend in backends]
            return dict(name=upstream_name,
                        servers=servs)

        def parse_servers():
            listens = set()
            server_names = list([default_name])
            is_ssl = True if protocol == 'ssl' else False
            default_server = False if backends else True
            listens.add((443 if is_ssl else 80, default_server, is_ssl))
            for entrypoint in getattr(balancer, 'entrypoints', []):
                server_names.append(entrypoint['domain'])
                is_ssl = True if entrypoint['protocol'] in ['ssl', 'https'] else False
                default_server = False if backends else True
                listens.add((443 if is_ssl else 80, default_server, is_ssl))
            listens = list(listens)
            listens.sort(key=lambda l: l[0])
            return dict(listens=listens,
                        server_names=server_names,
                        proxy_pass=upstream_name,
                        pattern='/')
        if protocol in protocol_support:
            upstreams.append(parse_upstream())
            servers.append(parse_servers())
    upstreams.sort(key=lambda ups: ups['name'])
    return upstreams, servers, list(ssl_files)
