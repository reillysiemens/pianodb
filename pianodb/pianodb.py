import multiprocessing
from datetime import timedelta

import requests
from lxml import html
from click import Command
from gunicorn.app.base import BaseApplication
from gunicorn.six import iteritems

from pianodb.model import Artist, Album, Song, Station, Play


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


def get_track_features(detail_url):
    xpath = ('//div[@class="song_features clearfix"]/text()|'
             '//div[@style="display: none;"]/text()')
    page = requests.get(detail_url)
    tree = html.fromstring(page.content)
    return [e.strip() for e in tree.xpath(xpath) if e.strip() != '']


def update_db(songfinish):
    # Search for the Artist, create it if necessary.
    artist = Artist.get_or_create(name=songfinish['artist'])[0]

    # Search for the Album, create it if necessary.
    album = Album.get_or_create(
        title=songfinish['album'],
        artist=artist,
        cover_art=songfinish['coverArt'])[0]

    detail_url = songfinish['detailUrl']

    # TODO: Actually store these features instead of just printing them.
    print(get_track_features(detail_url))

    # Search for the Song, create it if necessary.
    song = Song.get_or_create(
        title=songfinish['title'],
        album=album,
        duration=str(timedelta(seconds=int(songfinish['songDuration']))),
        detail_url=detail_url)[0]

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
    station = Station.get_or_create(name=songfinish['stationName'])[0]

    # Add the Artist to Station.artists if necessary.
    if artist not in station.artists:
        station.artists.add(artist)

    # Add the Song to Station.songs if necessary.
    if song not in station.songs:
        station.songs.add(song)

    # Create a new Play with an implicit timestamp of datetime.now()
    Play.create(
        station=station,
        song=song,
        duration=str(timedelta(seconds=int(songfinish['songPlayed']))))
