from sqlalchemy.engine import default
from sqlalchemy import pool
from sqlalchemy_teradata.compiler import TeradataCompiler, TeradataDDLCompiler, TeradataTypeCompiler
from sqlalchemy_teradata.base import TeradataIdentifierPreparer, TeradataExecutionContext
from sqlalchemy_teradata.base import ischema_names as ischema

class TeradataDialect(default.DefaultDialect):
    """
    Implements the Dialect interface. TeradataDialect inherits from the
       default.DefaultDialect. Changes made here are specific to Teradata where
       the default implementation isn't sufficient.

       Note that the default.DefaultDialect delegates some methods to the OdbcConnection
       in the tdodbc module passed in the dbapi class method

       """

    name = 'tdalchemy'
    driver = 'teradata'
    default_paramstyle = 'qmark'

    poolclass = pool.SingletonThreadPool
    statement_compiler = TeradataCompiler
    ddl_compiler = TeradataDDLCompiler
    type_compiler = TeradataTypeCompiler
    preparer = TeradataIdentifierPreparer
    execution_ctx_cls = TeradataExecutionContext


    ischema_names = ischema
    supports_native_boolean = False
    supports_native_decimal = True
    # convert_unicode = True
    encoding = 'utf-16'

    supports_unicode_statements = True
    supports_unicode_binds = True

    postfetch_lastrowid = False
    implicit_returning = False
    preexecute_autoincrement_sequences = False

    def __init__(self, **kwargs):
        super(TeradataDialect, self).__init__(**kwargs)

    def create_connect_args(self, url):
        if url is not None:
            params = super(TeradataDialect, self).create_connect_args(url)[1]
            return (("Teradata", params['host'], params['username'], params['password']), {})

    @classmethod
    def dbapi(cls):
        """ Hook to the dbapi2.0 implementation's module"""
        from teradata import tdodbc
        return tdodbc

    def has_table(self, connection, table_name, schema=None):
        q = 'select count(*) from dbc.tables where tablename=\'{}\''.format(table_name)
        res = connection.execute(q)
        row = res.fetchone()

        return row[0]
