
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
    def foreign_key_constraint_name_reflection(self):
        return exclusions.open()

    @property
    def table_ddl_if_exists(self):
        """target platform supports IF NOT EXISTS / IF EXISTS for tables."""
        return exclusions.open()

    @property
    def index_ddl_if_exists(self):
        """target platform supports IF NOT EXISTS / IF EXISTS for indexes."""
        return exclusions.closed()

    @property
    def deferrable_fks(self):
        """target database must support deferrable fks"""
        return exclusions.open()

    @property
    def foreign_key_constraint_option_reflection_ondelete(self):
        return exclusions.open()

    @property
    def fk_constraint_option_reflection_ondelete_restrict(self):
        return exclusions.open()

    @property
    def fk_constraint_option_reflection_ondelete_noaction(self):
        return exclusions.open()

    @property
    def foreign_key_constraint_option_reflection_onupdate(self):
        return exclusions.open()

    @property
    def fk_constraint_option_reflection_onupdate_restrict(self):
        return exclusions.open()

    @property
    def comment_reflection(self):
        return exclusions.open()

    @property
    def boolean_col_expressions(self):
        """Target database must support boolean expressions as columns"""
        return exclusions.open()

    @property
    def tuple_in(self):
        return exclusions.open()

    @property
    def update_from(self):
        """Target must support UPDATE..FROM syntax"""
        return exclusions.open()

    @property
    def delete_from(self):
        """Target must support DELETE FROM..FROM or DELETE..USING syntax"""
        return exclusions.open()

    @property
    def savepoints(self):
        """Target database must support savepoints."""
        return exclusions.open()

    @property
    def cross_schema_fk_reflection(self):
        """target system must support reflection of inter-schema foreign keys"""
        return exclusions.open()

    @property
    def implicit_default_schema(self):
        """target system has a strong concept of 'default' schema that can
        be referred to implicitly.
        """
        return exclusions.open()

    @property
    def default_schema_name_switch(self):
        return exclusions.open()

    @property
    def check_constraint_reflection(self):
        return exclusions.open()

    @property
    def indexes_with_expressions(self):
        return only_on(["greenplum >= 11"])

    @property
    def table_value_constructor(self):
        return exclusions.open()

    @property
    def ctes(self):
        """Target database supports CTEs"""
        return exclusions.open()

    @property
    def ctes_with_update_delete(self):
        """target database supports CTES that ride on top of a normal UPDATE
        or DELETE statement which refers to the CTE in a correlated subquery.
        """
        return exclusions.open()

    @property
    def ctes_on_dml(self):
        """target database supports CTES which consist of INSERT, UPDATE
        or DELETE *within* the CTE, e.g. WITH x AS (UPDATE....)"""
        return exclusions.open()

    @property
    def mod_operator_as_percent_sign(self):
        """target database must use a plain percent '%' as the 'modulus'
        operator."""
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
    def window_functions(self):
        return only_if(
            [
                "greenplum>=8.4",
            ],
            "Backend does not support window functions",
        )
    #
    # @property
    # def two_phase_transactions(self):
    #     """Target database must support two-phase transactions."""
    #
    #     def pg_prepared_transaction(config):
    #         if not against(config, "postgresql"):
    #             return True
    #
    #         with config.db.connect() as conn:
    #             try:
    #                 num = conn.scalar(
    #                     text(
    #                         "select cast(setting AS integer) from pg_settings "
    #                         "where name = 'max_prepared_transactions'"
    #                     )
    #                 )
    #             except exc.OperationalError:
    #                 return False
    #             else:
    #                 return num > 0
    #
    #     return skip_if(
    #         [
    #             NotPredicate(
    #                 LambdaPredicate(
    #                     pg_prepared_transaction,
    #                     "max_prepared_transactions not available or zero",
    #                 )
    #             ),
    #         ]
    #     )

    @property
    def two_phase_recovery(self):
        return self.two_phase_transactions

    @property
    def views(self):
        """Target database must support VIEWs."""
        return exclusions.open()

    @property
    def unicode_ddl(self):
        """Target driver must support some degree of non-ascii symbol names."""
        return exclusions.open()

    @property
    def nullsordering(self):
        """Target backends that support nulls ordering."""
        return exclusions.open()

    @property
    def reflects_pk_names(self):
        """Target driver reflects the name of primary key constraints."""
        return exclusions.open()

    @property
    def json_type(self):
        return only_on(
            [
                "greenplum >= 9.3",
            ]
        )

    @property
    def legacy_unconditional_json_extract(self):
        """Backend has a JSON_EXTRACT or similar function that returns a
        valid JSON string in all cases.
        Used to test a legacy feature and is not needed.
        """
        return exclusions.open()

    @property
    def reflects_json_type(self):
        return only_on(
            [
                "greenplum >= 9.3",
            ]
        )

    @property
    def datetime_timezone(self):
        return exclusions.open()

    @property
    def time_timezone(self):
        return exclusions.open()

    @property
    def datetime_historic(self):
        """target dialect supports representation of Python
        datetime.datetime() objects with historic (pre 1900) values."""
        return exclusions.open()

    @property
    def date_historic(self):
        """target dialect supports representation of Python
        datetime.datetime() objects with historic (pre 1900) values."""
        return exclusions.open()

    @property
    def precision_numerics_enotation_small(self):
        """target backend supports Decimal() objects using E notation
        to represent very small values."""
        # NOTE: this exclusion isn't used in current tests.
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
    def infinity_floats(self):
        return exclusions.open()

    @property
    def percent_schema_names(self):
        return exclusions.open()

    @property
    def ad_hoc_engines(self):
        return exclusions.closed()

    @property
    def computed_columns(self):
        return skip_if(["greenplum < 12"])

    @property
    def computed_columns_stored(self):
        return self.computed_columns

    @property
    def computed_columns_virtual(self):
        return exclusions.closed()

    @property
    def computed_columns_default_persisted(self):
        return self.computed_columns

    @property
    def computed_columns_reflect_persisted(self):
        return self.computed_columns

    @property
    def regexp_match(self):
        return exclusions.open()

    @property
    def regexp_replace(self):
        return exclusions.open()

    @property
    def supports_distinct_on(self):
        """If a backend supports the DISTINCT ON in a select"""
        return exclusions.open()

    @property
    def identity_columns(self):
        return only_if(["greenplum >= 10"])

    @property
    def identity_columns_standard(self):
        return self.identity_columns

    @property
    def index_reflects_included_columns(self):
        return only_on(["greenplum >= 11"])

    @property
    def fetch_first(self):
        return exclusions.open()

    @property
    def fetch_ties(self):
        return only_on(["greenplum >= 13"])

    @property
    def fetch_no_order_by(self):
        return exclusions.open()

    @property
    def fetch_offset_with_options(self):
        # use together with fetch_first
        return exclusions.open()

    @property
    def fetch_expression(self):
        # use together with fetch_first
        return exclusions.open()

    @property
    def reflect_tables_no_columns(self):
        # so far sqlite, mariadb, mysql don't support this
        return exclusions.open()
