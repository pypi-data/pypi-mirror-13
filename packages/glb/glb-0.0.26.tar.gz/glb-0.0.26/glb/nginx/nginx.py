# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from jinja2 import Environment, PackageLoader

from . import parser


JENV = Environment(loader=PackageLoader('glb.nginx', 'templates'))


def render(upstreams, servers):
    return (JENV
            .get_template('nginx.conf.jinja2')
            .render(upstreams=upstreams,
                    servers=servers))


def get_config(data):
    upstreams, servers, ssl_files = parser.parse(data)
    nginx_conf = render(upstreams, servers)
    return nginx_conf, ssl_files
