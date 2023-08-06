# $Id: image.py 08bc70c68510 2015/11/15 12:06:12 Patrick $
"""Web image opener."""

from os.path import basename, splitext
from webhelpers2.html import literal

from . import Opener as OpenerBase

OVERVIEW_IMAGE_HEIGHT = 48


# =============================================================================
class Opener(OpenerBase):
    """Class to operate on Web images."""
    # pylint: disable = locally-disabled, too-many-public-methods

    # -------------------------------------------------------------------------
    def match(self, fullname, content=None):
        """Check whether this opener matches with the file ``fullname``.

        See parent method :meth:`Opener.match`.
        """
        return splitext(fullname)[1] in (
            '.png', '.gif', '.jpg', '.jpeg', '.svg'), content

    # -------------------------------------------------------------------------
    def read(self, request, storage, path, content=None):
        """Literal XHTML to display the file content.

        See parent method :meth:`~.lib.opener.Opener.read`.
        """
        return literal(
            '<div><img src="%s" alt="%s"/></div>' %
            (request.route_path(
                'file_download', storage_id=storage['storage_id'], path=path),
             basename(path)))

    # -------------------------------------------------------------------------
    def overview(self, request, storage, path, content=None):
        """Return an abstract for the current file.

        See parent method :meth:`~.lib.opener.Opener.overview`.
        """
        return \
            '<img src="%s" height="%d" alt="%s"/>' \
            % (request.route_path(
                'file_download', storage_id=storage['storage_id'], path=path),
               OVERVIEW_IMAGE_HEIGHT, basename(path))

    # -------------------------------------------------------------------------
    @classmethod
    def can_write(cls):
        """Return ``True`` if it can simply modify the file.

        See parent method :meth:`~.lib.opener.Opener.can_write`.
        """
        return False

    # -------------------------------------------------------------------------
    @classmethod
    def css(cls, mode, request=None):
        """Return a list of CSS files for the mode ``mode``.

        See parent method :meth:`~.lib.opener.Opener.css`.
        """
        # pylint: disable = locally-disabled, unused-argument
        return tuple()

    # -------------------------------------------------------------------------
    @classmethod
    def javascript(cls, mode, request=None):
        """Return list of JavaScript files for the mode ``mode``.

        See parent method :meth:`~.lib.opener.Opener.javascript`.
        """
        # pylint: disable = locally-disabled, unused-argument
        return tuple()
