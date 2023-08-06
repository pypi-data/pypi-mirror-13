import json
import os

import click

from ndl import utils, filters

CONTEXT_SETTINGS = dict(help_option_names=['-h', '--help'])


def json_out(tree, options):
    click.echo(json.dumps(tree))


def flat_out(tree, options):
    for x in sorted(tree.keys()):
        for f in tree[x]:
            f_out = os.path.join(x, f)
            if not options.show_full_path:
                f_out = f_out.replace(options.basedir + os.path.sep, '')
            click.echo(f_out)

OUTPUT_FUNCS = {
    'json': json_out,
    'flat': flat_out,
}

def err_out(msg):
    click.echo(msg, err=True)


@click.command(context_settings=CONTEXT_SETTINGS)
@click.argument('path', default='.', type=click.Path(exists=True))
@click.option('-s', '--startswith', default=None)
@click.option('-e', '--endswith', default=None)
@click.option('-f', '--fuzzy', default=None, multiple=True)
@click.option('-i', '--ignore', default=None, multiple=True)
@click.option('--show-full-path/--hide-full-path', default=True)
@click.option('--fuzzy-include-dir', is_flag=True)
@click.option('-o', '--out-type', default='flat', type=click.Choice(['json', 'flat']))
def cli(
        path,
        startswith,
        endswith,
        fuzzy,
        ignore,
        out_type,
        show_full_path,
        fuzzy_include_dir):

    filter_options = utils.FilterOptions(
        fuzzy_include_dir=fuzzy_include_dir,
        show_full_path=show_full_path,
    )
    path = os.path.realpath(path)
    base_tree = utils.build_tree(path, filter_options, err_out=err_out)
    user_filters = []
    if ignore is not None:
        user_filters.extend((filters.IgnoreDir(x) for x in ignore))
    if endswith is not None:
        user_filters.append(filters.EndsWith(endswith))
        # user_filters.extend([filters.EndsWith(x) for x in  endswith])
    if startswith is not None:
        user_filters.append(filters.StartsWith(startswith))
        # user_filters.extend([filters.StartsWith(x) for x in startswith])
    if fuzzy is not None:
        user_filters.extend([filters.FuzzyMatch(x) for x in fuzzy])

    filtered_tree = utils.apply_filters(base_tree, user_filters, filter_options)
    filter_options.store_filters(user_filters)
    OUTPUT_FUNCS[out_type](filtered_tree, filter_options)
    filter_options.save()
