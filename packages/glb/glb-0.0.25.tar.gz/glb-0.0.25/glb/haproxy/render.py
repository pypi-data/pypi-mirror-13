# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from jinja2 import Environment, PackageLoader

from . import parser


JENV = Environment(loader=PackageLoader('glb.haproxy', 'templates'))


def render(frontends, backends):
    return (JENV
            .get_template('haproxy.cfg.jinja2')
            .render(wrapper_frontends=frontends,
                    wrapper_backends=backends))


def get_config(data):
    frontends, backends, pem_files = parser.parse(data)
    haproxy_conf = render(frontends, backends)
    return haproxy_conf, pem_files
