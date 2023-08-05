#!/usr/bin/env python3

"""
    PyHardLinkBackup cli using click
    ~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
"""


import os
import sys

# Use the built-in version of scandir/walk if possible, otherwise
# use the scandir module version
try:
    from os import scandir # new in Python 3.5
except ImportError:
    # use https://pypi.python.org/pypi/scandir
    try:
        from scandir import scandir
    except ImportError:
        raise ImportError("For Python <2.5: Please install 'scandir' !")

import click

import PyHardLinkBackup

from PyHardLinkBackup.phlb.config import phlb_config


@click.group()
@click.version_option(version=PyHardLinkBackup.__version__)
@click.pass_context
def cli(ctx):
    """PyHardLinkBackup"""
    click.secho("\nPyHardLinkBackup v%s\n" % PyHardLinkBackup.__version__,
        bg='blue', fg='white', bold=True
    )


@cli.command()
def helper():
    """
    setup helper files in venv root dir
    """
    BASE_DIR=os.path.abspath(os.path.dirname(PyHardLinkBackup.__file__))

    ENV_ROOT=os.path.normpath(os.path.join(os.path.dirname(sys.argv[0]), ".."))
    if not os.path.isdir(ENV_ROOT):
        raise RuntimeError("venv not found here: %r" % ENV_ROOT)

    if sys.platform.startswith("win"):
        # link batch files
        src_path = os.path.join(BASE_DIR, "helper_cmd")
    elif sys.platform.startswith("linux"):
        # link shell scripts
        src_path = os.path.join(BASE_DIR, "helper_sh")
    else:
        print("TODO: %s" % sys.platform)
        return

    if not os.path.isdir(src_path):
        raise RuntimeError("Helper script path not found here: %r" % src_path)

    for entry in scandir(src_path):
        print("_"*79)
        print("Link file: %r" % entry.name)
        src = entry.path
        dst = os.path.join(ENV_ROOT, entry.name)
        if os.path.exists(dst):
            print("Remove old file %r" % dst)
            try:
                os.remove(dst)
            except OSError as err:
                print("\nERROR:\n%s\n" % err)
                continue

        print("source.....: %r" % src)
        print("destination: %r" % dst)
        try:
            os.link(src, dst)
        except OSError as err:
            print("\nERROR:\n%s\n" % err)
            continue

cli.add_command(helper)


@click.command()
@click.option('--debug', is_flag=True, default=False,
              help="Display used config and exit.")
def config(debug):
    """Create/edit .ini config file"""
    if debug:
        phlb_config.print_config()
    else:
        phlb_config.open_editor()

cli.add_command(config)


@click.command()
def runserver():
    """Start django webserver with: 'manage runserver'"""
    raise RuntimeError("Please use 'manage.py' for this!")
cli.add_command(runserver)


@click.command()
def migrate():
    """Start django webserver with: 'manage migrate'"""
    raise RuntimeError("Please use 'manage.py' for this!")
cli.add_command(runserver)


@click.command()
@click.argument("path", type=click.Path(exists=True))
def backup(path):
    """Start a Backup run"""
    from PyHardLinkBackup.phlb.phlb_main import backup
    backup(path)

cli.add_command(backup)


if __name__ == '__main__':
    cli()
