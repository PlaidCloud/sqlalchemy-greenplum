#!/usr/bin/env python
# coding=utf-8

import sqlalchemy
from sqlalchemy.dialects.postgresql.base import (
    PGDialect, PGDDLCompiler
)
from sqlalchemy.dialects.postgresql.psycopg2 import PGDialect_psycopg2
import alembic_gp

class GreenplumDDLCompiler(PGDDLCompiler):
    """ Specific DDL Compiler for Greenplum

    Note:
        Inherits most of functionality from PGDDLCompiler
    """
    def post_create_table(self, table):
        """Process table creation options for Greenplum

        Note:
            This is overriding the PGDDLCompiler, so any postgresql options will NOT be processed using this dialect. The PostgreSQL options
            for "inherits", on_commit" and "tablespace" are replicated here though so can be specified in addition for Greenplum.
            Options for this dialect include (by example):
              greenplum_storage_params = 'OIDS=FALSE,APPENDONLY=TRUE' a string specifying the options (for now)
              greenplum_distributed_by = '"Name"' a string specifying the distribution fields
              greenplum_inherits = 'some_supertable'
              greenplum_on_commit = 'PRESERVE ROWS'
              greenplum_tablespace = 'MyTablespace'
        """
        table_opts = []
        gp_opts = table.dialect_options['greenplum']

        inherits = gp_opts.get('inherits')
        if inherits is not None:
            if not isinstance(inherits, (list, tuple)):
                inherits = (inherits, )
            table_opts.append(
                '\n INHERITS ( ' +
                ', '.join(self.preparer.quote(name) for name in inherits) +
                ' )')

        if gp_opts['storage_params']:
            table_opts.append(
                '\n WITH ({0})'.format(gp_opts['storage_params']).upper()
            )

        if gp_opts['on_commit']:
            on_commit_options = gp_opts['on_commit'].replace("_", " ").upper()
            table_opts.append('\n ON COMMIT %s' % on_commit_options)

        if gp_opts['tablespace']:
            tablespace_name = gp_opts['tablespace']
            table_opts.append(
                '\n TABLESPACE %s' % self.preparer.quote(tablespace_name)
            )

        if gp_opts['distributed_by']:
            if gp_opts['distributed_by'].upper() == 'RANDOM':
                table_opts.append('\n DISTRIBUTED RANDOMLY')
            else:
                table_opts.append('\n DISTRIBUTED BY ({0})'.format(gp_opts['distributed_by']))

        return ''.join(table_opts)

class GreenplumDialect(PGDialect_psycopg2):
    """Pivotal Greenplum Dialect

    Note:
       Inherits most of the functionality from PGDialect_psycopg2
    """
    name = 'greenplum'
    #supports_alter = True
    #max_identifier_length = 63
    #supports_sane_rowcount = True

    #supports_native_enum = True
    #supports_native_boolean = True
    #supports_smallserial = True

    #supports_sequences = True
    #sequences_optional = True
    #preexecute_autoincrement_sequences = True
    #postfetch_lastrowid = False

    #supports_default_values = True
    #supports_empty_insert = False
    #supports_multivalues_insert = True
    #default_paramstyle = 'pyformat'
    #ischema_names = ischema_names
    #colspecs = colspecs

    #statement_compiler = PGCompiler
    ddl_compiler = GreenplumDDLCompiler
    #type_compiler = PGTypeCompiler
    #preparer = PGIdentifierPreparer
    #execution_ctx_cls = PGExecutionContext
    #inspector = PGInspector
    #isolation_level = None

    construct_arguments = [
        (sqlalchemy.schema.Index, {
            "using": False,
            "where": None,
            "ops": {},
            "concurrently": False,
            "with": {},
            "tablespace": None
        }),
        (sqlalchemy.schema.Table, {
            "ignore_search_path": False,
            "tablespace": None,
            "storage_params": None,
            "on_commit": None,
            "inherits": None,
            "distributed_by": None
        }),
    ]

    #reflection_options = ('postgresql_ignore_search_path', )

    #_backslash_escapes = True
    #_supports_create_index_concurrently = True
    #_supports_drop_index_concurrently = True

    def __init__(self, *args, **kw):
        super(GreenplumDialect, self).__init__(*args, **kw)

    def initialize(self, connection):
        super(GreenplumDialect, self).initialize(connection)
        self.implicit_returning = False
            # self.server_version_info > (8, 2) and self.__dict__.get('implicit_returning', True)