#!/usr/bin/env python
# coding=utf-8

import sqlalchemy
import sqlalchemy.dialects.postgresql.base as base
from sqlalchemy.dialects.postgresql.psycopg2 import PGDialect_psycopg2, PGIdentifierPreparer_psycopg2
from sqlalchemy.sql import compiler, expression, coercions, roles
from sqlalchemy_greenplum import alembic_gp
import logging

# from https://github.com/greenplum-db/gpdb/blob/aa5fe3d52a20e26fb6883cad3d44bbe3addcb734/src/include/parser/kwlist.h
RESERVED_WORDS = {
    "all", "analyse", "analyze", "and", "any", "array", "as", "asc",
    "asymmetric", "both", "case", "cast", "check", "collate", "column",
    "constraint", "create", "current_catalog", "current_date",
    "current_role", "current_time", "current_timestamp", "current_user",
    "decode", "default", "deferrable", "desc", "distinct", "distributed",
    "do", "else", "end", "except", "exclude", "false", "fetch", "filter",
    "following", "for", "foreign", "from", "grant", "group", "having",
    "in", "initially", "intersect", "into", "leading", "limit",
    "localtime", "localtimestamp", "not", "null", "offset", "on", "only",
    "or", "order", "partition", "placing", "preceding", "primary",
    "references", "returning", "scatter", "select", "session_user",
    "some", "symmetric", "table", "then", "to", "trailing", "true",
    "unbounded", "union", "unique", "user", "using", "variadic", "when",
    "where", "window", "with",

    "authorization", "binary", "concurrently", "cross", "current_schema",
    "freeze", "full", "ilike", "inner", "is", "isnull", "join", "left",
    "like", "log", "natural", "notnull", "outer", "overlaps", "right",
    "similar", "verbose"
}

logger = logging.getLogger('sqlalchemy.dialects.postgresql')


class GreenplumDDLCompiler(base.PGDDLCompiler):
    """ Specific DDL Compiler for Greenplum

    Note:
        Inherits most of functionality from PGDDLCompiler
    """
    def post_create_table(self, table):
        """Process table creation options for Greenplum

        Note:
            This is overriding the PGDDLCompiler, so any postgresql options will NOT be processed using this dialect.
            The PostgreSQL options for "inherits", on_commit" and "tablespace" are replicated here though so can be
            specified in addition for Greenplum.
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
            elif gp_opts['distributed_by'].upper() == 'REPLICA':
                table_opts.append('\n DISTRIBUTED REPLICATED')
            else:
                table_opts.append('\n DISTRIBUTED BY ({0})'.format(gp_opts['distributed_by']))

        if gp_opts['partition_by']:
            table_opts.append('\n PARTITION BY %s' % gp_opts['partition_by'])

        return ''.join(table_opts)

    def visit_create_index(self, create):
        preparer = self.preparer
        index = create.element
        self._verify_index_table(index)
        text = "CREATE "
        if index.unique:
            distributed_by = index.table.dialect_options['greenplum']['distributed_by']
            # logger.info('table_cols={}'.format(str(index.table.columns)))
            if distributed_by is None:
                primary_key_cols = [c.name for c in index.table.primary_key]
                logger.info('primary_key_cols={}'.format(str(primary_key_cols)))
                distributed_by_cols = primary_key_cols
                if len(distributed_by_cols) == 0:
                    distributed_by_cols = [index.table.columns[0]]
            elif distributed_by == 'RANDOM':
                distributed_by_cols = []
            else:
                distributed_by_cols = distributed_by.split(',')
            logger.info('distributed_by_cols={}'.format(str(distributed_by_cols)))
            index_cols = [c.name for c in index.columns]
            logger.info('index_cols={}'.format(str(index_cols)))
            if set(index_cols).issuperset(set(distributed_by_cols)):
                text += "UNIQUE "
        text += "INDEX "

        if self.dialect._supports_create_index_concurrently:
            concurrently = index.dialect_options['greenplum']['concurrently']
            if concurrently:
                text += "CONCURRENTLY "

        if create.if_not_exists:
            text += "IF NOT EXISTS "

        text += "%s ON %s " % (
            self._prepared_index_name(index,
                                      include_schema=False),
            preparer.format_table(index.table)
        )

        using = index.dialect_options['greenplum']['using']
        if using:
            text += (
                "USING %s "
                % self.preparer.validate_sql_phrase(using, base.IDX_USING).lower()
            )

        ops = index.dialect_options["greenplum"]["ops"]
        text += "(%s)" \
                % (
                    ', '.join([
                        self.sql_compiler.process(
                            expr.self_group()
                            if not isinstance(expr, expression.ColumnClause)
                            else expr,
                            include_table=False,
                            literal_binds=True,
                        )
                        + (
                            (' ' + ops[expr.key])
                            if hasattr(expr, 'key')
                            and expr.key in ops else ''
                        )
                        for expr in index.expressions
                    ])
                )

        includeclause = index.dialect_options["greenplum"]["include"]
        if includeclause:
            inclusions = [
                index.table.c[col] if isinstance(col, str) else col
                for col in includeclause
            ]
            text += " INCLUDE (%s)" % ", ".join(
                [preparer.quote(c.name) for c in inclusions]
            )

        # nulls_not_distinct = index.dialect_options["greenplum"][
        #     "nulls_not_distinct"
        # ]
        # if nulls_not_distinct is True:
        #     text += " NULLS NOT DISTINCT"
        # elif nulls_not_distinct is False:
        #     text += " NULLS DISTINCT"

        withclause = index.dialect_options['greenplum']['with']

        if withclause:
            text += " WITH (%s)" % (', '.join(
                ['%s = %s' % storage_parameter
                 for storage_parameter in withclause.items()]))

        tablespace_name = index.dialect_options['greenplum']['tablespace']

        if tablespace_name:
            text += " TABLESPACE %s" % preparer.quote(tablespace_name)

        whereclause = index.dialect_options["greenplum"]["where"]

        if whereclause is not None:
            whereclause = coercions.expect(
                roles.DDLExpressionRole, whereclause
            )
            where_compiled = self.sql_compiler.process(
                whereclause,
                include_table=False,
                literal_binds=True,
            )
            text += " WHERE " + where_compiled
        return text

    def visit_drop_index(self, drop):
        index = drop.element

        text = "\nDROP INDEX "

        if self.dialect._supports_drop_index_concurrently:
            concurrently = index.dialect_options['greenplum']['concurrently']
            if concurrently:
                text += "CONCURRENTLY "

        text += self._prepared_index_name(index, include_schema=True)
        return text


class GreenplumCompiler(base.PGCompiler):
    pass
    # def format_from_hint_text(self, sqltext, table, hint, iscrud):
    #     if hint.upper() != 'ONLY':
    #         raise exc.CompileError("Unrecognized hint: %r" % hint)
    #     return "ONLY " + sqltext


class GreenplumIdentifierPreparer(PGIdentifierPreparer_psycopg2):
    reserved_words = RESERVED_WORDS


class GreenplumDialect(PGDialect_psycopg2):
    """Pivotal Greenplum Dialect

    Note:
       Inherits most of the functionality from PGDialect_psycopg2
    """
    name = 'greenplum'
    supports_statement_cache = True
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

    statement_compiler = GreenplumCompiler
    ddl_compiler = GreenplumDDLCompiler
    #type_compiler = PGTypeCompiler
    preparer = GreenplumIdentifierPreparer
    #execution_ctx_cls = PGExecutionContext
    #inspector = PGInspector
    #isolation_level = None

    construct_arguments = [
        (sqlalchemy.schema.Index, {
            "using": False,
            "include": None,
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
            "distributed_by": None,
            "partition_by": None
        }),
    ]

    #reflection_options = ('postgresql_ignore_search_path', )

    #_backslash_escapes = True
    _supports_create_index_concurrently = False
    _supports_drop_index_concurrently = True

    def __init__(self, *args, **kw):
        super(GreenplumDialect, self).__init__(*args, **kw)

    def initialize(self, connection):
        super(GreenplumDialect, self).initialize(connection)
        self.implicit_returning = False
            # self.server_version_info > (8, 2) and self.__dict__.get('implicit_returning', True)

    # def _get_server_version_info(self, connection):
    #     v = connection.execute("select version()").scalar()
    #     m = re.match(
    #         r'.*(?:PostgreSQL|EnterpriseDB) '
    #         r'(\d+)\.?(\d+)?(?:\.(\d+))?(?:\.\d+)?(?:devel|beta)?'
    #         r'?.*(Greenplum Database) '
    #         r'(\d+)\.?(\d+)?(?:\.(\d+))?(?:\.\d+)',
    #         v)
    #     if not m:
    #         raise AssertionError(
    #             "Could not determine version from string '%s'" % v)
    #     return tuple([int(x) for x in m.group(1, 2, 3) if x is not None])
