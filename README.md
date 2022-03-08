# SQLAlchemy dialect for Pivotal Greenplum

This dialect allows you to use the Pivotal Greenplum database with SQLAlchemy, extending the features
of the PostgreSQL dialect and adding in some Greenplum specific options. The install will also integrate
with Alembic for generation of migration scripts.

## Prerequisites

Python 3.X

### Installation
```
git clone https://github.com/PlaidCloud/sqlalchemy-greenplum.git
cd sqlalchemy-greenplum
python setup.py install
```

### Tests

To run the tests, alter the db entry in setup.cfg and create that database and a schema within it named 'test_schema' on the server
Then run from the project root folder
```
python setup.py test
```

There is a random failure for ServerSideCursorsTest_greenplum+psycopg2_8_3_23.test_roundtrip because it seems 
that Greenplum doesn't always return the records in the same order. Perhaps the test result needs to be ordered.

### Usage
```
    from sqlalchemy import create_engine
    engine = create_engine('greenplum://user:password@example.server.com')
    engine = create_engine('greenplum://user:password@example.server.com/example_database')
```

### Contribute

If you find any bugs or have any suggestions, you are welcome to create a GitHub Issue.

