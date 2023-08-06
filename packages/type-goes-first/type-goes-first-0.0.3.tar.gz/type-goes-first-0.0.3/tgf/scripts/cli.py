import click
import cligj
import json
from collections import OrderedDict


@click.command('tgf')
@cligj.features_in_arg
def cli(features):
    click.echo(json.dumps(
        OrderedDict([
            ('type', 'FeatureCollection'),
            ('features', list(features))])))
