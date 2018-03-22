# SQLAlchemy dialect for Pivotal Greenplum

This dialect allows you to use the Pivotal Greenplum database with SQLAlchemy, extending the features
of the PostgreSQL dialect and adding in some Greenplum specific options. The install will also integrate
with Alembic for generation of migration scripts.

## Prerequisites

Python 2.7 or Python 3.X

### Installation
```
git clone https://github.com/PlaidCloud/sqlalchemy-greenplum.git
cd sqlalchemy-greenplum
python setup.py install
```

### Usage
```
    from sqlalchemy import create_engine
    engine = create_engine('greenplum://user:password@example.server.com')
    engine = create_engine('greenplum://user:password@example.server.com/example_database')
```

### Contribute

If you find any bugs or have any suggestions, you are welcome to create a GitHub Issue.

