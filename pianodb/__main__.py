#!/usr/bin/env python3
import click

import pianodb.pianodb


@click.group(invoke_without_command=True)
@click.pass_context
def cli(ctx):
    if ctx.invoked_subcommand is None:
        click.echo('running main')


@cli.command()
def server():
    click.echo('running server')
