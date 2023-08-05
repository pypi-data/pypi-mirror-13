# coding: utf-8
import click

from .screenshots import ScreenShotsAPI


@click.group()
def cli():
    pass


def browserstacker_command(func):

    @cli.command(name=func.__name__)
    @click.option('--user', default=None, help='Username on BrowserStack.')
    @click.option('--key', default=None, help='Access key.')
    def wrapper(*args, **kwargs):
        return func(*args, **kwargs)

    return wrapper


@cli.command()
@click.option('--user', default=None, help='Username on BrowserStack.')
@click.option('--key', default=None, help='Access key.')
def list_browsers(user, key):
    click.echo(ScreenShotsAPI(user, key).list_browsers())


@cli.command()
@click.option('--user', default=None, help='Username on BrowserStack.')
@click.option('--key', default=None, help='Access key.')
@click.option('--job_id', default=None, help='Job ID to list screenshots')
def list_screenshots(user, key, job_id):
    click.echo(ScreenShotsAPI(user, key).list_screenshots(job_id))


@cli.command()
@click.option('--user', default=None, help='Username on BrowserStack.')
@click.option('--key', default=None, help='Access key.')
@click.option('--key', default=None, help='Access key.')
def make_screenshots(user, key):
    click.echo(ScreenShotsAPI(user, key).make_screenshots())
