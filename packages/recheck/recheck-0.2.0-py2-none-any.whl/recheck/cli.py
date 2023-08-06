import subprocess
import sys

import click
from recheck import requirements, textui as ui


@click.option('-r', '--requirements-file', metavar='PATH_TO_REQUIREMENTS_FILE',
              help='path to the requirements file')
@click.option('-i', '--ignore-file', metavar='PATH_TO_IGNORE_FILE',
              default='.recheckignore',
              help='path to the recheckignore file')
@click.command()
def main(requirements_file, ignore_file):
    if not requirements_file:
        raise click.BadOptionUsage('Must provide requirements file')

    requirements_parser = requirements.RequirementsParser(requirements_file)

    ignored_requirements = requirements.get_ignored_requirements(ignore_file)

    ignored, outdated_major, outdated_minor = set(), set(), set()
    for line in _list_oudated_requirements(requirements_parser.index_url,
                                           requirements_parser.extra_index_urls):
        ui.progress()
        req = requirements.parse_result(line)
        if not req:
            # the output does not resemble an outdated requirement
            continue

        if req.name not in requirements_parser.direct_requirements:
            # not a direct requirement
            continue

        requirements_file = requirements_parser.direct_requirements[req.name]

        req.requirements_file = requirements_file

        if req.name in ignored_requirements:
            ignored.add(req)
            continue

        if req.status == 'outdated:minor':
            outdated_minor.add(req)
            continue

        if req.status == 'outdated:major':
            outdated_major.add(req)
            continue

    ui.newline()

    _display_outdated_requirements('Minor upgrades:', outdated_minor, 'yellow')
    _display_outdated_requirements('Major upgrades:', outdated_major, 'red')

    if outdated_major or outdated_minor:
        sys.exit(1)
    else:
        ui.echo('OK', 'white')


def _build_pip_list_arg(index_url, extra_index_urls):
    args = ['pip', 'list', '--outdated']
    if index_url:
        args.append('--index-url={}'.format(index_url))

    if extra_index_urls:
        args.extend(['--extra-index-url={}'.format(extra_index_url)
                     for extra_index_url in extra_index_urls])

    return args


def _display_outdated_requirements(prompt, requirement_set, colour):
    if requirement_set:
        ui.echo(prompt, colour='white')

    for req in requirement_set:
        ui.render_requirement(req, colour=colour)

    ui.newline()


def _list_oudated_requirements(index_url, extra_index_urls):
    args = _build_pip_list_arg(index_url, extra_index_urls)
    proc = subprocess.Popen(args, stdout=subprocess.PIPE, stderr=subprocess.PIPE)
    return iter(proc.stdout.readline, '')
