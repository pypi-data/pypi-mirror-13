import click
from click.decorators import _make_command

from signal import signal, SIGPIPE, SIG_DFL
from prody import confProDy, LOGGER
from .rmsd import srmsd, pwrmsd
from .prep import clean, splitsegs, psfgen, nmin, prep, pdb_psf_concat
from .util import config
from .cluspro import submit, _apply_ftresult

from .. import __version__

signal(SIGPIPE, SIG_DFL)
LOGGER._setverbosity(confProDy('verbosity'))

VERBOSITY = 0


@click.option('-v', '--verbose', count=True)
@click.version_option(version=__version__)
def sblu(verbose):
    global VERBOSITY
    VERBOSITY = verbose


cli = _make_command(sblu, 'sblu', {}, cls=click.Group)
cli.add_command(srmsd)
cli.add_command(pwrmsd)
cli.add_command(clean)
cli.add_command(splitsegs)
cli.add_command(psfgen)
cli.add_command(nmin)
cli.add_command(prep)
cli.add_command(pdb_psf_concat)

cli.add_command(config)
cli.add_command(submit)
cli.add_command(_apply_ftresult)
