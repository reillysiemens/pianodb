import os
from urllib.parse import urlparse
import pytest
from playhouse.db_url import connect
from pianodb.pianodb import create_database


@pytest.fixture(scope='module', params=[
    'sqlite:////tmp/pianodb-test.db',
    'mysql://root@127.0.0.1:3306/pianodb_test',
    'postgres://postgres@127.0.0.1:5432/pianodb_test',
])
def database(request):
    """
    A fixture for setting up and tearing down SQLite, MySQL, and PostgreSQL
    databases using ``playhouse.db_url.connect``.

    TODO:
        Figure out how to teardown MySQL and PostgreSQL databases.

    Note:
        ``playhouse.db_url.connect`` requires four forward slashes in the SQLite
        URI for some reason.
    """
    database = connect(request.param)

    yield database

    if 'sqlite' in request.param:
        parsed_uri = urlparse(request.param)
        os.remove(parsed_uri.path)


def test_pianodb_can_create_database(database):
    """
    Test that ``pianodb`` can create a database.
    """
    create_database(database)
