# coding: utf-8

import click
import json
import os
import requests
import subprocess
import time

STATION_URL = 'http://radioglobo.globo.com/global/api/gradeTransmissoes.php'
PLAYLIST_URL = 'http://radioglobo.globo.com/playlist/asxJWAovivo.php'


def get_stations():
    req = requests.get(STATION_URL, params={'_': int(time.time())})
    if not req.ok:
        raise click.ClickException('Failed to get stations.')
    j = req.json()
    if not j:
        raise click.ClickException('Failed to parse stations from website.')
    rv = j.keys()
    rv.sort()
    return rv


def get_media_urls(station):
    req = requests.get(PLAYLIST_URL, params={'praca': station,
                                             'formatoPlaylist': 'JSON',
                                             '_': int(time.time())})
    if not req.ok:
        raise click.ClickException('Failed to get playlist.')
    j = req.json()
    if not j:
        raise click.ClickException('Failed to parse playlist from website.')
    return [i['file'] for i in j if 'file' in i]


@click.group()
def cli():
    '''Script to play radioglobo.globo.com radio streaming in the shell.'''


@cli.command()
def stations():
    '''Lists available radioglobo.globo.com stations.'''
    click.echo('Available stations:')
    click.echo()
    for station in get_stations():
        click.echo('\t%s' % station)


@cli.command()
@click.argument('station')
def play(station):
    '''Plays a radioglobo.globo.com station.'''
    stations = get_stations()
    if station not in stations:
        raise click.ClickException('Invalid station: %s' % station)
    urls = get_media_urls(station)
    if not urls:
        raise click.ClickException('No streaming found for stations: %s' %
                                   station)
    click.echo('Playing station: %s' % station)
    click.echo()
    rv = subprocess.call(['mpv', urls[0]])
    if rv != os.EX_OK:
        click.ClickException('Failed to run mpv (%d): %s' % (rv, urls[0]))


if __name__ == '__main__':
    cli()
