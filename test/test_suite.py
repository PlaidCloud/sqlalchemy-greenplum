# # coding: utf-8


from sqlalchemy.testing.suite import *
from sqlalchemy.testing.assertions import AssertsCompiledSQL
from sqlalchemy import Table, Column, Integer, MetaData, select
from sqlalchemy import schema


class CompileTest(fixtures.TestBase, AssertsCompiledSQL):

    __only_on__ = "greenplum"

    def test_create_table_with_oids(self):
        m = MetaData()
        tbl = Table(
            'atable', m, Column("id", Integer),
            greenplum_storage_params='OIDS=TRUE', )
        self.assert_compile(
            schema.CreateTable(tbl),
            "CREATE TABLE atable (id INTEGER) WITH (OIDS=TRUE)")

        tbl2 = Table(
            'anothertable', m, Column("id", Integer),
            greenplum_storage_params='OIDS=FALSE')
        self.assert_compile(
            schema.CreateTable(tbl2),
            "CREATE TABLE anothertable (id INTEGER) WITH (OIDS=FALSE)")

    def test_create_table_with_storage_params(self):
        m = MetaData()
        tbl = Table(
            'atable', m, Column("id", Integer),
            greenplum_storage_params='APPENDONLY=TRUE')
        self.assert_compile(
            schema.CreateTable(tbl),
            "CREATE TABLE atable (id INTEGER) WITH (APPENDONLY=TRUE)")

    def test_create_table_with_multiple_storage_params(self):
        m = MetaData()
        tbl = Table(
            'atable', m, Column("id", Integer),
            greenplum_storage_params='APPENDONLY=TRUE,OIDS=FALSE,ORIENTATION=COLUMN')
        self.assert_compile(
            schema.CreateTable(tbl),
            "CREATE TABLE atable (id INTEGER) WITH (APPENDONLY=TRUE,OIDS=FALSE,ORIENTATION=COLUMN)")

    def test_create_table_with_distibuted_by(self):
        m = MetaData()
        tbl = Table(
            'atable', m, Column("id", Integer),
            greenplum_distributed_by='"ID"')
        self.assert_compile(
            schema.CreateTable(tbl),
            "CREATE TABLE atable (id INTEGER) DISTRIBUTED BY (\"ID\")")

    def test_create_table_with_multiple_options(self):
        m = MetaData()
        tbl = Table(
            'atable', m, Column("id", Integer),
            greenplum_tablespace='sometablespace',
            greenplum_storage_params='OIDS=FALSE',
            greenplum_on_commit='preserve_rows',
            greenplum_distributed_by='"ID"')
        self.assert_compile(
            schema.CreateTable(tbl),
            "CREATE TABLE atable (id INTEGER) WITH (OIDS=FALSE) "
            "ON COMMIT PRESERVE ROWS TABLESPACE sometablespace "
            "DISTRIBUTED BY (\"ID\")")

    def test_reserved_words(self):
        table = Table("pg_table", MetaData(),
                      Column("col1", Integer),
                      Column("variadic", Integer))
        x = select(table.c.col1, table.c.variadic)

        self.assert_compile(
            x,
            '''SELECT pg_table.col1, pg_table."variadic" FROM pg_table''')

    def test_greenplum_reserved_words(self):
        table = Table("pg_table", MetaData(),
                      Column("col1", Integer),
                      Column("log", Integer))
        x = select(table.c.col1, table.c.log)

        self.assert_compile(
            x,
            '''SELECT pg_table.col1, pg_table."log" FROM pg_table''')
