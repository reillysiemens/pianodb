import pytest
import msgpack
from falcon import API, testing

from pianodb.routes import ValidatorComponent, SongFinish


TOKEN = 'CB80CB12CC0F41FC87CA6F2AC989E27E'
API_PREFIX = '/api/v1'
SONGFINISH_ROUTE = "{API_PREFIX}/songfinish".format(API_PREFIX=API_PREFIX)


@pytest.fixture(scope='module')
def client():

    api = API(middleware=ValidatorComponent())
    api.add_route(SONGFINISH_ROUTE, SongFinish(token=TOKEN))

    return testing.TestClient(api)


def test_songfinish_requires_auth_token(client):
    """
    TODO: Document this test.
    """

    expected = dict(
        title='Authentication required',
        description='Missing or invalid authentication token',
    )

    result = client.simulate_post(path=SONGFINISH_ROUTE)

    assert result.status_code == 401  # HTTP 401 Unauthorized
    assert result.json == expected


def test_songfinish_requires_msgpack_payloads(client):
    """
    TODO: Document this test.
    """

    expected = dict(
        title='Unsupported media type',
        description='Payload must be msgpack',
    )

    result = client.simulate_post(path=SONGFINISH_ROUTE,
                                  headers={
                                      'X-Auth-Token': TOKEN,
                                  })

    assert result.status_code == 415  # HTTP 415 Unsupported Media Type
    assert result.json == expected


def test_songfinish_requires_valid_msgpack_payloads(client):
    """
    TODO: Document this test.
    """

    # A properly formatted payload would be b'\x81\xa6artist\xabJohn Cleese'
    malformed_msgpack = b'\x82\xa6artist\xabJohn Cleese'

    expected = dict(
        title='Bad request',
        description='Could not unpack msgpack data',
    )

    result = client.simulate_post(path=SONGFINISH_ROUTE,
                                  body=malformed_msgpack,
                                  headers={
                                      'X-Auth-Token': TOKEN,
                                      'Content-Type': 'application/msgpack',
                                  })

    assert result.status_code == 400  # HTTP 400 Bad Request
    assert result.json == expected


# TODO: Test remaining branches and investigate msgpack.exceptions.ExtraData or
# UnicodeDecodeError errors when given a non-msgpack request body.
