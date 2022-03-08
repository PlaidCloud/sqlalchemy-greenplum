
import os
from setuptools import setup, find_packages

source_location = os.path.abspath(os.path.dirname(__file__))


def get_version():
    with open(os.path.join(source_location, "VERSION")) as version:
        return version.readline().strip()


setup(
    name="sqlalchemy-greenplum",
    version=get_version(),
    license="LICENSE.txt",
    url="https://github.com/PlaidCloud/sqlalchemy-greenplum",
    author="Patrick Buxton",
    author_email="patrick.buxton@tartansolutions.com",
    description="SQLAlchemy dialect for Pivotal Greenplum Database",
    long_description="SQLAlchemy dialect for Pivotal Greenplum Database",
    long_description_content_type="text/markdown",
    packages=find_packages(),
    zip_safe=False,
    install_requires=[
        "sqlalchemy"
    ],
    extras_require={
    },
    setup_requires=["pytest-runner"],
    tests_require=["pytest", "mock"],
    test_suite="test.test_suite",
    classifiers=[ # cf. http://pypi.python.org/pypi?%3Aaction=list_classifiers
        "Development Status :: 2 - Pre-Alpha",
        "Intended Audience :: Developers",
        "License :: Other/Proprietary License",
        "Operating System :: OS Independent",
        "Programming Language :: Python",
        "Programming Language :: Python :: 3",
        "Programming Language :: Python :: 3.7",
        "Programming Language :: Python :: 3.8",
        "Programming Language :: Python :: 3.9",
        "Programming Language :: Python :: 3.10",
        "Programming Language :: Python :: Implementation :: PyPy",
        "Programming Language :: SQL",
        "Topic :: Database",
        "Topic :: Database :: Front-Ends",
        "Topic :: Software Development",
        "Topic :: Software Development :: Libraries :: Python Modules",
    ],
    entry_points={
        "sqlalchemy.dialects": [
            "greenplum = sqlalchemy_greenplum.dialect:GreenplumDialect",
            "greenplum.psycopg2 = sqlalchemy_greenplum.dialect:GreenplumDialect"
        ]
    },
)
