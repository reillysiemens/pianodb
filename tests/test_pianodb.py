"""
TODO:
    Implement a test that proves file configs override rather than overwrite
    the defaults. Unfortunately this functionality will have to be implemented
    first.
"""

import os
from unittest import mock

import pytest
import requests

from pianodb.pianodb import (number_of_workers, gen_dummy_cmd, get_config,
                             get_track_features)


class MockPage:
    def __init__(self, status_code=200, content=''):
        self.status_code = status_code
        self.content = content if content else """
<!-- https://www.pandora.com/great-jazz-trio/s-wonderful/take-5 -->
<div class="artist_name" title="The Great Jazz Trio">
  <span>by</span>
  <span itemprop="byArtist">
    <a href="/great-jazz-trio" class="artist_link hash">The Great Jazz Trio</a>
  </span>
</div>
<div class="album_title" title="'S Wonderful">
  <span>on</span>
  <a href="/great-jazz-trio/s-wonderful" itemprop="inAlbum" class="album_link hash">'S Wonderful</a>
</div>
<div class="song_features clearfix">
  <h2>Features of This Track</h2>
  a piano solo<br>
  an acoustic bass solo<br>
  a groove oriented approach<br>
  vamping harmony<br>
  <div style="display: none;">
    unusual rhythms<br>
  </div>
  <p>These are just a few of the hundreds of attributes cataloged for this track by the Music Genome Project.</p>
  <a href="#" class="show_more">show more</a>
</div>
"""


@mock.patch('pianodb.pianodb.multiprocessing')
def test_pianodb_number_of_workers_is_double_cpu_count_plus_one(mp):
    """
    Test that ``pianodb`` determines the number of workers to be double the CPU
    count plus one.

    Note:
        This test patches the multiprocessing.cpu_count function to return a
        constant that does not depend on the actual CPU count.
    """
    mp.cpu_count.return_value = 6

    assert number_of_workers() == 13


def test_pianodb_can_generate_dummy_click_commands():
    """
    Test that ``pianodb`` can generate dummy instances of ``Click.Command`` that
    have the correct ``name``, ``help``, and ``short_help``.
    """
    cmd = gen_dummy_cmd('dummy')

    assert cmd.name == 'dummy'
    assert cmd.help == ("This is an unimplimented pianobar eventcmd handler. "
                        "Calling this subcommand will do absolutely nothing.")
    assert cmd.short_help == 'unimplimented pianobar eventcmd'


@mock.patch.dict(os.environ, {'HOME': '/home/cleesej'})
@mock.patch('builtins.open', create=True)
@mock.patch('tempfile.gettempdir')
@mock.patch('pianodb.pianodb.multiprocessing')
def test_pianodb_has_config_defaults(mp, tmpdir, mock_open):
    """
    Test that ``pianodb`` has config defaults that are used when getting its
    configuration. In the absence of an option defined in a config file the
    ``pianodb`` config should contain these defaults.
    """
    database = '/home/cleesej/.config/pianobar/piano.db'
    server_database = '/faketmp/piano.db'

    # Pretend we have a CPU count of 4.
    mp.cpu_count.return_value = 4

    # Pretend we have a fake temp dir.
    tmpdir.return_value = '/faketmp'

    # Pretend open will read a file with nothing in it.
    mock_open.side_effect = [
        mock.mock_open(read_data="").return_value,
    ]

    # This is probably a good rationale for having a global default config dict.
    expected_config = {
        'client': {
            'remote': None,
            'threshold': 10,
            'token': None,
            'database': database,
        },
        'server': {
            'interface': 'localhost',
            'port': 8000,
            'workers': 9,
            'database': server_database,
        }
    }

    # overrides: os.environ, os.path, open, multiprocessing.cpu_count
    config = get_config()
    assert config == expected_config

@mock.patch.dict(os.environ, {'HOME': '/home/cleesej'})
@mock.patch('builtins.open', create=True)
@mock.patch('tempfile.gettempdir')
@mock.patch('pianodb.pianodb.multiprocessing')
def test_pianodb_can_load_configs_from_optional_path(mp, tmpdir, mock_open):
    """
    Test that ``pianodb`` can load a config file from a path other than
    its own internal default by using the optional ``path`` argument.
    """

    # Pretend we have a CPU count of 8.
    mp.cpu_count.return_value = 8

    # Pretend we have a fake temp dir.
    tmpdir.gettempdir.return_value = '/faketmp'

    # Pretend open will read a file with nothing in it.
    mock_open.side_effect = [
        mock.mock_open(read_data="").return_value,
    ]

    config = get_config(path='/spam/and/eggs')

    mock_open.assert_called_once_with('/spam/and/eggs', 'r')


@mock.patch.dict(os.environ, {'HOME': '/home/cleesej'})
def test_pianodb_exits_fatally_without_a_config_file():
    """
    Test that ``pianodb`` raises a ``SystemExit`` error with the appropriate
    error message when attempting to load a nonexistent config.
    """
    with pytest.raises(SystemExit) as err:
        config = get_config(path='nonexistent')
    assert str(err.value) == 'could not load config'


def test_pianodb_can_get_track_features(monkeypatch):
    """
    Test that ``pianodb`` can extract track features from a specially formatted
    web page.
    """

    def _mock_page(url):
        return MockPage()

    monkeypatch.setattr(requests, 'get', _mock_page)

    expected = [
        'a piano solo',
        'an acoustic bass solo',
        'a groove oriented approach',
        'vamping harmony',
        'unusual rhythms',
    ]

    assert get_track_features('https://fake-url.tld') == expected


def test_pianodb_track_features_empty_if_status_code_is_not_200(monkeypatch):
    """
    Test that ``pianodb`` track features are empty when ``requests`` returns
    a ``status_code`` that is not ``200``.
    """

    def _mock_page(url):
        return MockPage(status_code=418, content='teapot')

    monkeypatch.setattr(requests, 'get', _mock_page)

    assert get_track_features('https://fake-url.tld') == []


def test_pianodb_track_features_empty_if_requests_connection_error(monkeypatch):
    """
    Test that ``pianodb`` track features are empty when ``requests`` raises a
    ``ConnectionError``.
    """

    def _raise_connection_error(url):
        raise requests.ConnectionError()

    monkeypatch.setattr(requests, 'get', _raise_connection_error)

    assert get_track_features('https://fake-url.tld') == []
