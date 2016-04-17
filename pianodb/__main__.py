#!/usr/bin/env python3
import click
import falcon

import pianodb.model
from pianodb.pianodb import number_of_workers, PianoDBApplication
from pianodb.routes import SongFinish

API_PREFIX = '/api/v1'


@click.group(invoke_without_command=True)
@click.pass_context
def cli(ctx):

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

    if ctx.invoked_subcommand is None:
        click.echo('running main')


@cli.command()
def server():

    options = {
        'bind': "{}:{}".format('127.0.0.1', '8000'),
        'workers': number_of_workers(),
    }

    api = falcon.API()
    api.add_route("{}/songfinish".format(API_PREFIX), SongFinish())

    PianoDBApplication(api, options).run()
