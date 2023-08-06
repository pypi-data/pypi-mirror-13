from collections import OrderedDict

import click
import json

import tgf


@click.command('tgf')
@click.argument('input', default='-', required=False)
def cli(input):
    try:
        input = click.open_file(input).readlines()
    except IOError:
        input = [input]

    click.echo(json.dumps(OrderedDict([
        ('type', 'FeatureCollection'),
        ('features', [json.loads(f) for f in input])
        ])))
