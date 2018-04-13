
import sys
from sqlalchemy import util
from sqlalchemy.testing.requirements import SuiteRequirements
from sqlalchemy.testing import exclusions
from sqlalchemy.testing.exclusions import \
     skip, \
     skip_if,\
     only_if,\
     only_on,\
     fails_on_everything_except,\
     fails_on,\
     fails_if,\
     succeeds_if,\
     SpecPredicate,\
     against,\
     LambdaPredicate,\
     requires_tag


class Requirements(SuiteRequirements):
    @property
    def returning(self):
        return exclusions.closed()

    @property
    def table_reflection(self):
        return exclusions.open()

    @property
    def duplicate_key_raises_integrity_error(self):
        return exclusions.closed()

    @property
    def temp_table_reflection(self):
        return exclusions.closed()

    @property
    def primary_key_constraint_reflection(self):
        return exclusions.open()

    @property
    def reflects_pk_names(self):
        return exclusions.open()
    
    @property
    def order_by_col_from_union(self):
        return exclusions.open()
    
    @property
    def independent_connections(self):
        return exclusions.open()

    @property
    def implicitly_named_constraints(self):
        return exclusions.open()

    @property
    def foreign_key_constraint_option_reflection_ondelete(self):
        return exclusions.open()

    @property
    def foreign_key_constraint_option_reflection_onupdate(self):
        return exclusions.open()

    @property
    def comment_reflection(self):
        return exclusions.open()

    @property
    def identity(self):
        return exclusions.closed()

    @property
    def reflectable_autoincrement(self):
        return exclusions.open()

    @property
    def tuple_in(self):
        return exclusions.open()

    @property
    def isolation_level(self):
        return exclusions.open()

    @property
    def autocommit(self):
        return exclusions.open()

    @property
    def row_triggers(self):
        return exclusions.closed()

    @property
    def update_from(self):
        return exclusions.open()

    @property
    def delete_from(self):
        return exclusions.open()

    @property
    def views(self):
        """Target database must support VIEWs."""
        return exclusions.open()

    @property
    def schemas(self):
        """Target database must support external schemas, and have one named 'test_schema'.
        """
        return exclusions.open()

    @property
    def implicit_default_schema(self):
        return exclusions.open()

    @property
    def cross_schema_fk_reflection(self):
        """target system must support reflection of inter-schema foreign keys
        """
        return exclusions.open()

    @property
    def unique_constraint_reflection(self):
        # for version 5.4 gp .... usually open for PG server_version...
        return exclusions.closed()

    @property
    def unique_constraint_reflection_no_index_overlap(self):
        return self.unique_constraint_reflection

    @property
    def check_constraint_reflection(self):
        # for version 5.4 gp .... usually open for PG server_version...
        return exclusions.closed()

    @property
    def temporary_views(self):
        """target database supports temporary views"""
        return exclusions.open()

    @property
    def update_nowait(self):
        """Target database must support SELECT...FOR UPDATE NOWAIT"""
        return exclusions.open()

    @property
    def ctes(self):
        """Target database supports CTEs"""
        return exclusions.open()

    @property
    def ctes_on_dml(self):
        """target database supports CTES which consist of INSERT, UPDATE or DELETE"""
        return exclusions.open()

    @property
    def mod_operator_as_percent_sign(self):
        """target database must use a plain percent '%' as the 'modulus' operator."""
        return exclusions.open()

    @property
    def intersect(self):
        """Target database must support INTERSECT or equivalent."""
        return exclusions.open()

    @property
    def except_(self):
        """Target database must support EXCEPT or equivalent (i.e. MINUS)."""
        return exclusions.open()

    @property
    def order_by_col_from_union(self):
        """target database supports ordering by a column from a SELECT inside of a UNION"""
        return exclusions.open()

    @property
    def window_functions(self):
        return exclusions.closed() # for GP 5.4
        # return only_if([
        #             "postgresql>=8.4", "mssql", "oracle"
        #         ], "Backend does not support window functions")

    @property
    def two_phase_transactions(self):
        """Target database must support two-phase transactions."""
        return exclusions.open()

    @property
    def two_phase_recovery(self):
        return self.two_phase_transactions

    @property
    def unicode_ddl(self):
        """Target driver must support some degree of non-ascii symbol names."""
        return exclusions.open()

    @property
    def dbapi_lastrowid(self):
        """"target backend includes a 'lastrowid' accessor on the DBAPI
        cursor object.
        """
        return exclusions.closed() #For GP5.4

    @property
    def nullsordering(self):
        """Target backends that support nulls ordering."""
        return exclusions.open()

    @property
    def array_type(self):
        return exclusions.open()

    @property
    def json_type(self):
        return exclusions.closed() #for GP5.4

    @property
    def datetime_historic(self):
        """target dialect supports representation of Python
        datetime.datetime() objects with historic (pre 1970) values."""

        return exclusions.open()

    @property
    def date_historic(self):
        """target dialect supports representation of Python
        datetime.datetime() objects with historic (pre 1970) values."""

        return exclusions.open()

    @property
    def precision_numerics_enotation_small(self):
        """target backend supports Decimal() objects using E notation
        to represent very small values."""
        # NOTE: this exclusion isn't used in current tests.
        return exclusions.open()

    @property
    def precision_numerics_enotation_large(self):
        """target backend supports Decimal() objects using E notation
        to represent very large values."""
        return exclusions.open()

    @property
    def precision_numerics_many_significant_digits(self):
        """target backend supports values with many digits on both sides,
        such as 319438950232418390.273596, 87673.594069654243
        """
        return exclusions.open()

    @property
    def precision_numerics_retains_significant_digits(self):
        """A precision numeric type will return empty significant digits,
        i.e. a value such as 10.000 will come back in Decimal form with
        the .000 maintained."""

        return exclusions.open()

    @property
    def precision_generic_float_type(self):
        """target backend will return native floating point numbers with at
        least seven decimal places when using the generic Float type."""

        return exclusions.open()

    def _has_pg_extension(self, name):
        def check(config):
            count = config.db.scalar(
                "SELECT count(*) FROM pg_extension "
                "WHERE extname='%s'" % name)
            return bool(count)
        return only_if(check, "needs %s extension" % name)

    @property
    def hstore(self):
        return self._has_pg_extension("hstore")

    @property
    def btree_gist(self):
        return self._has_pg_extension("btree_gist")

    @property
    def range_types(self):
        def check_range_types(config):
            try:
                config.db.scalar("select '[1,2)'::int4range;")
                return True
            except Exception:
                return False

        return only_if(check_range_types)

    @property
    def postgresql_test_dblink(self):
        return exclusions.open()
        # return skip_if(
        #             lambda config: not config.file_config.has_option(
        #                 'sqla_testing', 'postgres_test_db_link'),
        #             "postgres_test_db_link option not specified in config"
        #         )

    @property
    def postgresql_jsonb(self):
        return exclusions.closed()
        # return only_on("postgresql >= 9.4") + skip_if(
        #     lambda config:
        #     config.db.dialect.driver == "pg8000" and
        #     config.db.dialect._dbapi_version <= (1, 10, 1)
        # )

    @property
    def psycopg2_native_json(self):
        return self.psycopg2_compatibility

    @property
    def psycopg2_native_hstore(self):
        return self.psycopg2_compatibility

    @property
    def psycopg2_compatibility(self):
        return exclusions.open()

    @property
    def psycopg2_or_pg8000_compatibility(self):
        return exclusions.open()

    # def get_order_by_collation(self, config):
    #     return "POSIX"

    @property
    def python_fixed_issue_8743(self):
        return exclusions.skip_if(
            lambda: sys.version_info < (2, 7, 8),
            "Python issue 8743 fixed in Python 2.7.8"
        )

    @property
    def postgresql_utf8_server_encoding(self):
        return only_if(
            config.db.scalar("show server_encoding").lower() == "utf8"
        )