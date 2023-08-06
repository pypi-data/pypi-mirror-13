# $Id: publidoc2csv_make_id.py 5c1135f02e94 2015/03/07 12:28:49 Patrick $
"""LePrisme make_id script."""

from os.path import basename, splitext

from publiforge.lib.utils import make_id as utils_make_id


# =============================================================================
def make_id(fullname, build, config):
    """Fill pack.

    :param fullname: (string)
        Absolute path to the original file to transform.
    :param build: (:class:`publiforge.lib.build.agent.AgentBuild` instance)
        Main Build object.
    :param config: (:class:`ConfigParser.ConfigParser` instance)
        Object to access to the processor configuration file.
    """
    # pylint: disable=locally-disabled, unused-argument
    return '%s_special' % utils_make_id(
        splitext(basename(fullname))[0], 'token')
