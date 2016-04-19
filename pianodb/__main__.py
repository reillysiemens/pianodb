#!/usr/bin/env python3
import os
import sys
import json
import os.path

import click
import falcon
import msgpack
import requests

import pianodb.model
from pianodb.pianodb import number_of_workers, gen_dummy_cmd, PianoDBApplication
from pianodb.routes import SongFinish

API_PREFIX = '/api/v1'

# Notice the conspicuously absent 'songfinish' event.
EVENTS = (
    'artistbookmark',
    'songban',
    'songbookmark',
    'songexplain',
    'songlove',
    'songmove',
    'songshelf',
    'songstart',
    'stationaddgenre',
    'stationaddmusic',
    'stationaddshared',
    'stationcreate',
    'stationdelete',
    'stationdeleteartistseed',
    'stationdeletefeedback',
    'stationdeletesongseed',
    'stationfetchgenre',
    'stationfetchinfo',
    'stationfetchplaylist',
    'stationquickmixtoggle',
    'stationrename',
    'usergetstations',
    'userlogin',
)


@click.group(commands={e: gen_dummy_cmd(e) for e in EVENTS})
@click.pass_context
def cli(ctx):

    if ctx.invoked_subcommand in ('server', 'songfinish'):
        # Connect to DB, potentially creating tables, regardless of subcommand.
        tables = (
            pianodb.model.Artist,
            pianodb.model.Album,
            pianodb.model.Song,
            pianodb.model.Feature,
            pianodb.model.SongFeature,
            pianodb.model.Station,
            pianodb.model.StationArtist,
            pianodb.model.StationSong,
            pianodb.model.Play
        )

        pianodb.model.db.connect()
        pianodb.model.db.create_tables(tables, safe=True)


@cli.command(help=("songfinish is the handler for pianobar's `songfinish' "
                   "eventcmd. It reads event fields from stdin and, depending "
                   "on configuration creates local database entries or sends "
                   "data to a remote server."),
             short_help='songfinish eventcmd handler')
@click.option('--debug', is_flag=True)
def songfinish(debug):

    if debug:
        click.echo('Debugging...')

    home = os.environ['HOME']

    config_path = os.path.join(home, '.config', 'pianobar', 'pianodb.json')

    with open(config_path, 'r') as cf:
        config = json.load(cf)

    fields = dict(line.strip().split('=', 1) for line in sys.stdin)

    if not fields['artist']:
        sys.exit('Artist is empty. Refusing to continue.')

    if int(fields['songPlayed']) >= config['threshold']:
        songfinish_data = {
            'artist': fields['artist'],
            'title': fields['title'],
            'album': fields['album'],
            'coverArt': fields['coverArt'],
            'stationName': fields['stationName'],
            'songDuration': fields['songDuration'],
            'songPlayed': fields['songPlayed'],
            'rating': fields['rating'],
            'detailUrl': fields['detailUrl'].split('?')[0]  # sans query string
        }

        url = "http://{}:{}/api/v1/songfinish".format(config['host'],
                                                      config['port'])
        r = requests.post(
            url,
            data=msgpack.packb(songfinish_data),
            headers={
                'X-Auth-Token': config['token'],
                'Content-Type': 'application/msgpack'
            })

        if not r.ok:
            click.echo('Something went wrong with the request.')


@cli.command(help=("server starts a Gunicorn webserver with a minimal Falcon "
                   "WSGI application. It listens for POST requests of "
                   "MessagePack data to create database entries."),
             short_help='start a pianodb webserver')
@click.option('--debug', is_flag=True)
def server(debug):

    if debug:
        click.echo('Debugging...')

    options = {
        'bind': "{}:{}".format('127.0.0.1', '8000'),
        'workers': number_of_workers(),
    }

    api = falcon.API()
    api.add_route("{}/songfinish".format(API_PREFIX), SongFinish())

    PianoDBApplication(api, options).run()
