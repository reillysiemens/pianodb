#!/usr/bin/env python3
import sys

import click
import falcon
import msgpack
import requests

import pianodb.model
from pianodb.pianodb import get_config, gen_dummy_cmd, PianoDBApplication
from pianodb.routes import SongFinish

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

        ctx.obj = get_config()

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

        pianodb.model.db.init(ctx.obj['client']['database'])
        pianodb.model.db.connect()
        pianodb.model.db.create_tables(tables, safe=True)


@cli.command(help=("songfinish is the handler for pianobar's `songfinish' "
                   "eventcmd. It reads event fields from stdin and, depending "
                   "on configuration creates local database entries or sends "
                   "data to a remote server."),
             short_help='songfinish eventcmd handler')
@click.option('--debug', is_flag=True)
@click.pass_context
def songfinish(ctx, debug):

    if debug:
        click.echo('Debugging...')

    config = ctx.obj['client']

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

        if config['remote']:
            host = config['remote']['host']
            port = config['remote']['port']
            url = "http://{}:{}/api/v1/songfinish".format(host, port)
            r = requests.post(
                url,
                data=msgpack.packb(songfinish_data),
                headers={
                    'X-Auth-Token': config['token'],
                    'Content-Type': 'application/msgpack'
                })

            if not r.ok:
                click.echo('Something went wrong with the request.')
        else:
            sys.exit('local usage not yet implemented')


@cli.command(help=("server starts a Gunicorn webserver with a minimal Falcon "
                   "WSGI application. It listens for POST requests of "
                   "MessagePack data to create database entries."),
             short_help='start a pianodb webserver')
@click.option('--debug', is_flag=True)
@click.pass_context
def server(ctx, debug):

    if debug:
        click.echo('Debugging...')

    config = ctx.obj['server']

    options = {
        'bind': "{}:{}".format(config['interface'], config['port']),
        'workers': config['workers'],
    }

    api = falcon.API()
    api.add_route("{}/songfinish".format(config['api_prefix']), SongFinish())

    PianoDBApplication(api, options).run()
