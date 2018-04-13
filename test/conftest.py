

from sqlalchemy.dialects import registry

registry.register("greenplum", "sqlalchemy_greenplum.dialect", "GreenplumDialect")

from sqlalchemy.testing.plugin.pytestplugin import *
