import sys
import os.path
import tempfile
import multiprocessing
from datetime import timedelta
from collections import ChainMap

import requests
import ruamel.yaml
from lxml import html
from click import Command
from gunicorn.app.base import BaseApplication
from gunicorn.six import iteritems

import pianodb.model as model


class PianoDBApplication(BaseApplication):
    """http://docs.gunicorn.org/en/latest/custom.html"""
    def __init__(self, app, options=None):
        self.options = options or {}
        self.application = app
        super().__init__()

    def load_config(self):
        config = dict([(key, value) for key, value in iteritems(self.options)
                       if key in self.cfg.settings and value is not None])
        for key, value in iteritems(config):
            self.cfg.set(key.lower(), value)

    def load(self):
        return self.application


def number_of_workers():
    return (multiprocessing.cpu_count() * 2) + 1


def gen_dummy_cmd(name):
    return Command(name,
                   help=("This is an unimplimented pianobar eventcmd handler. "
                         "Calling this subcommand will do absolutely nothing."),
                   short_help='unimplimented pianobar eventcmd')


def get_config(path=None):
    home = os.environ['HOME']
    pianobar_path = os.path.join(home, '.config', 'pianobar')
    pianodb_config_path = os.path.join(pianobar_path, 'pianodb.yml')

    path = path if path else pianodb_config_path

    try:
        with open(path, 'r') as config_path:
            config = ruamel.yaml.load(config_path)
    except (FileNotFoundError, PermissionError):
        sys.exit('could not load config')

    defaults = {
        'client': {
            'remote': None,
            'threshold': 10,
            'token': None,
            'database': os.path.join(pianobar_path, 'piano.db')
        },
        'server': {
            'interface': 'localhost',
            'port': 8000,
            'workers': number_of_workers(),
            'database': os.path.join(tempfile.gettempdir(), 'piano.db'),
        }
    }

    return ChainMap(config, defaults)


def get_track_features(detail_url):
    xpath = ('//div[@class="song_features clearfix"]/text()|'
             '//div[@style="display: none;"]/text()')
    try:
        page = requests.get(detail_url)
        if page.status_code == 200:
            tree = html.fromstring(page.content)
            return [e.strip() for e in tree.xpath(xpath) if e.strip() != '']
        else:
            return []
    except requests.ConnectionError:
        return []


def create_database(database):
    tables = (
        model.Artist,
        model.Album,
        model.Song,
        model.Feature,
        model.SongFeature,
        model.Station,
        model.StationArtist,
        model.StationSong,
        model.Play
    )

    model.db.initialize(database)
    model.db.connect()
    model.db.create_tables(tables, safe=True)


def update_db(songfinish):
    # Search for the Artist, create it if necessary.
    artist = model.Artist.get_or_create(name=songfinish['artist'])[0]

    # Search for the Album, create it if necessary.
    # Take into account that cover_art is always subject to change and we want
    # to prefer whatever Pandora says is most recent.
    try:
        album = model.Album.get(model.Album.title == songfinish['album']
                                and model.Album.artist == artist)
        album.cover_art = songfinish['coverArt']
        album.save()
    except model.Album.DoesNotExist:
        album = model.Album.create(
            title=songfinish['album'],
            artist=artist,
            cover_art=songfinish['coverArt'])

    detail_url = songfinish['detailUrl']

    # Search for the Song, create it if necessary.
    song = model.Song.get_or_create(
        title=songfinish['title'],
        album=album,
        duration=str(timedelta(seconds=int(songfinish['songDuration']))),
        detail_url=detail_url)[0]

    # Search for the Features, create them if necessary.
    features = [model.Feature.get_or_create(text=f)[0]
                for f in get_track_features(detail_url)]

    # Add the Features to Song.features if necessary.
    for feature in features:
        if feature not in song.features:
            song.features.add(feature)

    # Search for the Station, create it if necessary.
    # TODO: Investigate whether Station is correct at time of songfinish.
    #       Something appears to be wrong when switching stations. It causes
    #       crap like this to end up in the DB.
    #
    #       sqlite> select * from song;
    #       ...
    #       8||8|0:02:26
    #       ...
    #       42||8|0:03:05
    station = model.Station.get_or_create(name=songfinish['stationName'])[0]

    # Add the Artist to Station.artists if necessary.
    if artist not in station.artists:
        station.artists.add(artist)

    # Add the Song to Station.songs if necessary.
    if song not in station.songs:
        station.songs.add(song)

    # Create a new Play with an implicit timestamp of datetime.now()
    model.Play.create(
        station=station,
        song=song,
        duration=str(timedelta(seconds=int(songfinish['songPlayed']))))
