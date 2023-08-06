"""A *processor* use a module to realize its processing."""

from os import environ
from os.path import join, dirname
from sys import executable
from lxml import etree

from ..utils import _


# =============================================================================
def load_relaxngs(build, config):
    """Load Relax NG files defined in configuration.

    :param build: (:class:`~.lib.build.agent.AgentBuild`)
        Main Build object.
    :param config: (:class:`ConfigParser.ConfigParser` instance)
        Configuration with a ``[RelaxNG]`` section.
    :return: (dictionary)
        A dictionary of :class:`lxml.etree.RelaxNG` objets.
    """
    relaxngs = {}
    if not config.has_section('RelaxNG'):
        return relaxngs

    for root, filename in config.items('RelaxNG'):
        if root not in ('here', 'fid', 'ocffile'):
            root = root.replace('|', ':')
            try:
                relaxngs[root] = etree.RelaxNG(etree.parse(filename))
            except IOError as err:
                build.stopped(err)
                return relaxngs
            except (etree.XMLSyntaxError, etree.RelaxNGParseError) as error:
                build.stopped(
                    _('${f}: ${e}', {'f': filename, 'e': error}))
                return relaxngs
    return relaxngs


# =============================================================================
def bin_directory():
    """Return absolute path to PubliForge binary directory."""
    return \
        'VIRTUAL_ENV' in environ and join(environ['VIRTUAL_ENV'], 'bin') \
        or dirname(executable)
