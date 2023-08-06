# $Id: publidoc2csv1_pre.py cb61e393af47 2015/03/02 17:15:25 Patrick $
"""LePrisme preprocess script."""

from publiforge.lib.utils import _


# =============================================================================
def main(processor, filename, fid, data):
    """Preprocess script.

    :param processor: (:class:`Processor` instance)
        Processor object.
    :param filename: (string)
        Relative path to the original file to transform.
    :param fid: (string)
        File identifier.
    :param data: (string or :class:`lxml.etree.ElementTree` object)
        Data to transform in a string or in a tree.
    :return: (string, :class:`lxml.etree.ElementTree` object or ``None``)
        Modified data or ``None`` if fails.
    """
    # pylint: disable = locally-disabled, unused-argument
    processor.build.log(_('${f}: dummy preprocess of "${f}"', {'f': fid}))
    return data
