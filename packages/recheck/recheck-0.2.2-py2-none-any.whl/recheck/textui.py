import sys
import click


def echo(txt, colour):
    click.echo(click.style(txt, fg=colour))


def render_requirement(r, colour):
    click.echo(click.style('{:20} {:10} -> {:10}'.format(
        '{}/{}'.format(r.requirements_file, r.name),
        r.installed_version, r.remote_version), fg=colour))


def progress(indicator='.'):
    sys.stderr.write(indicator)


def newline():
    sys.stderr.write('\n')
