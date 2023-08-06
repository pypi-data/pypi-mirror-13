"""
Command line scripts.
"""

import click
import os

from .parsers import read_context_from_url
from .index import Index


def pinfo(msg, *args, **kwargs):
    click.secho(str(msg).format(*args, **kwargs), fg='white')


@click.command(
    help="Generate code from a collection of templates and a context file.",
)
@click.option(
    '-d',
    '--debug',
    is_flag=True,
    help="Enable debug output and traceback logging. Use this when something "
    "is not working and you really can't figure out what from the error "
    "messages only.",
)
@click.option(
    '-o',
    '--output-root',
    type=click.Path(exists=False),
    default='output',
    help="The default output directory to put generated files in. If no "
    "output directory is specified, the default `output` is used.",
)
@click.option(
    '-t',
    '--target',
    'targets',
    type=str,
    multiple=True,
    help="A target to build. Can be repeated multiple times. If no target "
    "is specified, the default targets are used. If no default targets are "
    "defined, all targets are used.",
)
@click.argument('index-file', type=click.File())
@click.argument('context-url', type=click.Path(dir_okay=False))
def pygen(debug, output_root, targets, index_file, context_url):
    context = read_context_from_url(context_url)
    index = Index.load(cwd=os.path.dirname(index_file.name), stream=index_file)

    try:
        os.makedirs(output_root)
    except OSError:
        pass

    for target_name, filename, content in index.generate(context=context):
        output_filename = os.path.join(output_root, filename)

        pinfo(
            '{target_name}: -> {filename}',
            target_name=target_name,
            filename=output_filename,
        )

        with open(output_filename, 'w') as file:
            file.write(content)
