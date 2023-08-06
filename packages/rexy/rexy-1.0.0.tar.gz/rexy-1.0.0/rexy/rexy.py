# coding:utf-8

import cgi
from wexy import Wexy
from .cached import cached
from .group import Group

try:
    from urlparse import parse_qs
except ImportError:
    from urllib.parse import parse_qs


class Rexy(object):
    def __init__(self, environ):
        self._environ = Wexy(environ)
        self._cache = {}

    @property
    def environ(self):
        return self._environ

    @cached
    def fieldstorage(self):
        return cgi.FieldStorage(environ=self.environ.environ,
                                fp=self.environ.wsgi_input)

    @cached
    def query(self):
        qs = self.environ.query_string or ''
        return Group(parse_qs(qs))

    @cached
    def cookie(self):
        qs = self.environ.http_cookie or ''
        return Group(parse_qs(qs))

    @cached
    def body(self):
        mapping = {}
        if isinstance(self.fieldstorage.value, list):
            for k in self.fieldstorage:
                obj = self.fieldstorage[k]
                if isinstance(obj, list):
                    mapping[k] = []
                    for fs in obj:
                        if fs.filename is None:
                            mapping[k].append(fs.value)

                        else:
                            mapping[k].append(fs)

                else:
                    if obj.filename is None:
                        mapping[k] = [obj.value]

                    else:
                        mapping[k] = [obj]

        return Group(mapping)
