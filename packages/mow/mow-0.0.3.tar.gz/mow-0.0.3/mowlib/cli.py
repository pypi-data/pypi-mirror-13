import mowlib as mlb
import click
import os
import sys
from mowlib import configuration

pass_config = click.make_pass_decorator(configuration.Config, ensure=True)


@click.group()
@click.option('--verbose', '-v', type=int, default=0, help="verbose")
@click.option('--preview', '-p', is_flag=True, help="preview")
@click.option('--trace', '-t', type=int, default=0, help='Include a trace in output')
@pass_config
def cli(config, verbose, preview, trace):
    config.verbose = verbose
    configuration.verbose = verbose
    configuration.trace = trace
    config.preview = preview


@cli.command()
@click.option('--reset-cache', '-r', is_flag=True, help="Reset (delete) the cache before scanning")
@click.argument('input', type=click.Path(), required=True)
@click.argument('output', type=click.Path(), required=True)
@click.argument('unknown', type=click.Path(), required=True)
@pass_config
def scan(config, reset_cache, input, output, unknown):
    if input == output:
        sys.exit("Error: input and output cannot be the same")

    config.input_folder = os.path.realpath(input)
    config.output_folder = os.path.realpath(output)
    config.unknown_folder = os.path.realpath(unknown)

    cache = mlb.Cache(configuration.application_name, configuration.movie_cache_filename,
                      remove_cache=reset_cache)
    statistics = mlb.Statistics()

    if config.verbose > 0:
        click.echo("cache-location: {}".format(mlb.param_name(cache.filename)))
        click.echo("appname: {}".format(mlb.param_name(mlb.application_name)))
        click.echo("Scanning folders, input {}, output {}".format(mlb.path_in(input), mlb.path_out(output)))

    mlb.process_folder(config, root=config.input_folder, cache=cache, stats=statistics)
    cache.write()
    if config.verbose > 0:
        print("{}".format(statistics.string_output()))
        sys.exit()

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
