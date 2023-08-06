import mowlib as mlb
import click
import os
import sys
from mowlib import configuration

pass_config = click.make_pass_decorator(configuration.Config, ensure=True)


def print_version(ctx, param, value):
    if not value or ctx.resilient_parsing:
        return
    click.echo('{}, version {} - by @schpaencoder'.format(mlb.application_name, mlb.__version__))
    ctx.exit()


@click.group()
@click.option('--version', '-V', is_flag=True, callback=print_version,
              expose_value=False, is_eager=True, help="Show version information.")
@click.option('--verbose', '-v', type=click.Choice(['0', '1', '2', '3']), default='0',
              help="Verbose output, higher number indicates more output.")
@click.option('--trace', '-t', type=int, default=0, help='Include a trace in output, number indicates depth of calls.')
@pass_config
def cli(config, verbose, trace):
    '''
    Organise your movies without setting your hair on fire
    '''
    config.verbose = int(verbose)
    configuration.verbose = int(verbose)
    configuration.trace = trace


@cli.command()
@click.option('--reset-cache', '-r', is_flag=True, help="Reset (delete) the cache before scanning")
@click.option('--preview', '-p', is_flag=True, help="Previews paths, but generates no output.")
@click.argument('input', type=click.Path(), required=True)
@click.argument('output', type=click.Path(), required=True)
@click.argument('unknown', type=click.Path(), required=False)
@pass_config
def scan(config, reset_cache, preview, input, output, unknown):
    config.preview = preview

    if unknown is None:
        unknown = os.path.join(output, 'unknown')

    if input == output:
        sys.exit("Error: input and output cannot be the same")

    config.input_folder = os.path.realpath(input)
    config.output_folder = os.path.realpath(output)
    config.unknown_folder = os.path.realpath(unknown)

    if config.verbose > 0 or config.verbose > 2:
        if reset_cache:
            click.echo('Will remove cache at: {}'.format(
                mlb.param_name(mlb.cache_filename(configuration.application_name, configuration.movie_cache_filename))))

    if config.preview or config.verbose > 2:
        click.echo("Input folder: {}".format(mlb.param_name(config.input_folder)))
        click.echo("Output folder: {}".format(mlb.param_name(config.output_folder)))
        click.echo("Folder for unrecognized files: {}".format(mlb.param_name(config.unknown_folder)))
        if config.preview:
            sys.exit()

    cache = mlb.Cache(configuration.application_name, configuration.movie_cache_filename,
                      remove_cache=reset_cache)
    statistics = mlb.Statistics()

    if config.verbose > 1:
        click.echo("cache-location: {}".format(mlb.param_name(cache.filename)))
        click.echo("appname: {}".format(mlb.param_name(mlb.application_name)))
        click.echo("Scanning folders, input {}, output {}".format(mlb.path_in(input), mlb.path_out(output)))

    mlb.process_folder(config, root=config.input_folder, cache=cache, stats=statistics)
    cache.write()
    if config.verbose > 0:
        print("{}".format(statistics.string_output()))
        sys.exit()

@cli.command()
@pass_config
def list(config):
    cache = mlb.Cache(configuration.application_name, configuration.movie_cache_filename,
                      remove_cache=False)
    cache.restore()
    mlb.show_list(config, cache)


# @cli.command()
# @click.option('--input-folder', '-i', default=".", type=click.Path(), help="input path")
# @click.option('--output-folder', '-o', default="output", type=click.Path(), help="output path")
# @click.option('--string')
# @click.argument('out', type=click.File('w'), default='-', required=False)
# @pass_config
# def create(config, input_folder, output_folder, string, out):
#     input_folder = os.path.realpath(input_folder)
#     output_folder = os.path.realpath(output_folder)
#
#     config.input_folder = input_folder
#     config.output_folder = output_folder
#
#     click.echo(Fore.LIGHTYELLOW_EX + config.input_folder)
#     click.echo(Fore.LIGHTYELLOW_EX + config.output_folder)
#
#     if config.verbose:
#         click.echo(Fore.BLACK + Back.LIGHTYELLOW_EX + " We are in verbose mode " + Back.RESET)
#     click.echo(Fore.BLUE + Back.RESET + "hello, everything working?", file=out)
#
#
# @cli.command()
# @click.option('--string')
# @click.argument('out', type=click.File('w'), default='-', required=False)
# @pass_config
# def list(config, string, out):
#     print(config)
#     if config.verbose:
#         click.echo(Fore.BLACK + Back.LIGHTYELLOW_EX + " We are in verbose mode ")
#     click.echo(Fore.BLUE + Back.RESET + "hello, everything working?", file=out)

# @cli.group()
# @pass_config
# def clone(config):
#     # ctx.obj = Config()
#     print(config)
#     pass


# @clone.command()
# @click.option('--ex', is_flag=True, help="help-text")
# @pass_config
# def jalla(config, ex):
#     print(config.list())
