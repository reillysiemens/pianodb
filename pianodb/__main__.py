#!/usr/bin/env python3
import sys

import click
import falcon
import msgpack
import requests

from pianodb.pianodb import get_config, gen_dummy_cmd, create_db, update_db, PianoDBApplication
from pianodb.routes import ValidatorComponent, SongFinish

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
    cmd = ctx.invoked_subcommand

    if cmd in ('songfinish', 'server'):
        config = get_config()
        ctx.obj = config['server'] if cmd == 'server' else config['client']

        if 'database' in ctx.obj:
            create_db(ctx.obj['database'])


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

    config = ctx.obj

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

        if 'remote' in config:
            try:
                host = config['remote']['host']
                port = config['remote']['port']
            except KeyError:
                sys.exit('missing parameters for communication with remote')
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
            update_db(songfinish_data)


@cli.command(help=("server starts a Gunicorn webserver with a minimal Falcon "
                   "WSGI application. It listens for POST requests of "
                   "MessagePack data to create database entries."),
             short_help='start a pianodb webserver')
@click.option('--debug', is_flag=True)
@click.pass_context
def server(ctx, debug):

    if debug:
        click.echo('Debugging...')

    config = ctx.obj

    options = {
        'bind': "{}:{}".format(config['interface'], config['port']),
        'workers': config['workers'],
    }

    songfinish_route = "{}/songfinish".format(config['api_prefix'])

    api = falcon.API(middleware=ValidatorComponent())
    api.add_route(songfinish_route, SongFinish(config['token']))

    PianoDBApplication(api, options).run()
