import os
from playhouse.db_url import connect
from pianodb.pianodb import create_database


def test_create_sqlite():
    # Setup the database.
    db_path = '/tmp/piano-test.db'
    db_uri = "sqlite:///{}".format(db_path)
    database = connect(db_uri)
    create_database(database)

    # Teardown the database.
    os.remove(db_path)


def test_create_mysql():
    # Setup the database.
    db_uri = 'mysql://root@127.0.0.1:3306/pianodb_test'
    database = connect(db_uri)
    create_database(database)

    # TODO: Figure out how to "tear down" the MySQL database...


def test_create_postgresql():
    # Setup the database.
    db_uri = 'postgres://postgres@127.0.0.1:5432/pianodb_test'
    database = connect(db_uri)
    create_database(database)

    # TODO: Figure out how to "tear down" the PostgreSQL database...
