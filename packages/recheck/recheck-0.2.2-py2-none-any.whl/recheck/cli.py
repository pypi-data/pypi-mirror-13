import subprocess
import sys

import click
from recheck import requirements, textui


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
        textui.progress()
        requirement = requirements.parse_result(line)
        if not requirement:
            # the output does not resemble an outdated requirement
            continue

        if requirement.name not in requirements_parser.direct_requirements:
            continue

        requirements_file = requirements_parser.direct_requirements[requirement.name]

        requirement.requirements_file = requirements_file

        if requirement.name in ignored_requirements:
            ignored.add(requirement)
            continue

        if requirement.status == 'outdated:minor':
            outdated_minor.add(requirement)
        elif requirement.status == 'outdated:major':
            outdated_major.add(requirement)

    textui.newline()

    _display_outdated_requirements('Minor upgrades:', outdated_minor, 'yellow')
    _display_outdated_requirements('Major upgrades:', outdated_major, 'red')

    if outdated_major or outdated_minor:
        sys.exit(1)
    else:
        textui.echo('OK', 'white')


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
        textui.echo(prompt, colour='white')

    for req in requirement_set:
        textui.render_requirement(req, colour=colour)

    textui.newline()


def _list_oudated_requirements(index_url, extra_index_urls):
    args = _build_pip_list_arg(index_url, extra_index_urls)
    proc = subprocess.Popen(args, stdout=subprocess.PIPE, stderr=subprocess.PIPE)
    return iter(proc.stdout.readline, '')
