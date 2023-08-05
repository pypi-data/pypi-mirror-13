#! /usr/bin/env python
# -*- coding: utf-8 -*-
from __future__ import unicode_literals


def parse(data):
    if not data:
        data = []
    open_ports = set()
    temp_data = {}
    wrapper_frontends = []
    wrapper_backends = []
    pem_files = set()
    for balancer in data:
        balancer_name = balancer.name

        def parse_frontend():
            port = balancer.frontend.get('port')
            mode = balancer.frontend.get('protocol', 'http')
            open_ports.add(port)
            frontend = dict(balancer_name=balancer_name,
                            port=port,
                            mode=mode,
                            domains=list(),
                            pems=list())
            temp_data[port] = frontend

        def parse_entrypoints():

            def parse_certificate():
                pem_file_names = []
                if 'certificate' in entrypoint.keys():
                    private_key = entrypoint['certificate']['private_key']
                    certificate_chain = entrypoint['certificate']['certificate_chain']
                    pfile_name = '%s_%s' % (balancer_name, domain)
                    pem_files.add((pfile_name, private_key, certificate_chain))
                    pem_file_names.append(pfile_name)
                return pem_file_names

            for entrypoint in getattr(balancer, 'entrypoints', []):
                domain = entrypoint.get('domain')
                port = entrypoint.get('port')
                mode = entrypoint.get('protocol')
                if port in open_ports:
                    wrapper_domain = dict(domain=domain,
                                          backend_name=balancer_name)
                    temp_data[port]['domains'].append(wrapper_domain)
                    parse_certificate()
                    temp_data[port]['pems'].extend(parse_certificate())
                else:
                    frontend = dict(
                        balancer_name=balancer_name,
                        port=port,
                        mode=mode,
                        domains=list([dict(domain=domain,
                                           backend_name=balancer_name)]),
                        pems=list())
                    frontend['pems'].extend(parse_certificate())
                    temp_data[port] = frontend

        def parse_backend():
            return (dict(name=balancer_name,
                         mode=balancer.frontend.get('protocol', 'http'),
                         backends=getattr(balancer, 'backends', [])))
        parse_frontend()
        parse_entrypoints()
        wrapper_backends.append(parse_backend())
    wrapper_frontends = temp_data.values()
    wrapper_frontends.sort(key=lambda frontend: frontend['port'])
    wrapper_backends.sort(key=lambda backends: backends['name'])
    return wrapper_frontends, wrapper_backends, list(pem_files)
