import sys
import click


def echo(txt, colour):
    click.echo(click.style(txt, fg=colour))


def render_requirement(r, colour):
    click.echo(click.style('{:12} {:8} -> {:8}'.format(r.name, r.installed_version, r.remote_version), fg=colour))


def progress(indicator='.'):
    sys.stderr.write(indicator)


def newline():
    sys.stderr.write('\n')
