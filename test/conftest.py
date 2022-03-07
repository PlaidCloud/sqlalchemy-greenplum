
import pytest
from sqlalchemy.dialects import registry

registry.register("greenplum+psycopg2", "sqlalchemy_greenplum.dialect", "GreenplumDialect")
registry.register("greenplum", "sqlalchemy_greenplum.dialect", "GreenplumDialect")
pytest.register_assert_rewrite("sqlalchemy.testing.assertions")

from sqlalchemy.testing.plugin.pytestplugin import *
