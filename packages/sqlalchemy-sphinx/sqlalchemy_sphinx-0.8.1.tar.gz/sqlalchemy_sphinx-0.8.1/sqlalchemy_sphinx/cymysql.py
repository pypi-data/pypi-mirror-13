""" CyMySQL connector"""

from __future__ import absolute_import

import cymysql
from cymysql.connections import Connection
from sqlalchemy.dialects.mysql import cymysql as cymysql_dialect
from sqlalchemy_sphinx.dialect import SphinxDialect

__all__ = ("Dialect",)


class DBAPIShim(object):

    def connect(self, *args, **kwargs):
        return Connection(*args, **kwargs)

    def __getattr__(self, name):
        return getattr(cymysql, name)


class Dialect(SphinxDialect, cymysql_dialect.MySQLDialect_cymysql):

    def _get_default_schema_name(self, connection):
        pass

    def _detect_charset(self, connection):
        pass

    def _detect_casing(self, connection):
        pass

    def _detect_collations(self, connection):
        pass

    def _detect_ansiquotes(self, connection):
        self._server_ansiquotes = False

    def get_isolation_level(self, connection):
        pass

    @classmethod
    def dbapi(cls):
        return DBAPIShim()
