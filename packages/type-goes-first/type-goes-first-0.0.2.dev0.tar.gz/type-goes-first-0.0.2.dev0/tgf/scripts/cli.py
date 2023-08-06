import click
import cligj
import json

@click.command('tgf')
@cligj.features_in_arg
def cli(features):
    click.echo(json.dumps(
        {'type': 'FeatureCollection',
         'features': list(features)}))
