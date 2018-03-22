from sqlalchemy.ext.compiler import compiles

try:
    from alembic.ddl import postgresql
except ImportError:
    pass
else:
    from alembic.ddl.base import AlterColumn, RenameTable
    compiles(AlterColumn, 'greenplum')(postgresql.visit_column_type)
    compiles(RenameTable, 'greenplum')(postgresql.visit_rename_table)

    class GreenplumImpl(postgresql.PostgresqlImpl):
        __dialect__ = 'greenplum'
        transactional_ddl = True