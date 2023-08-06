# $Id: home.py 8aad2a4a050d 2016/01/03 10:16:12 Patrick $
# pylint: disable = locally-disabled, C0322
"""Home view callables."""

from os.path import join, dirname

from pyramid.view import view_config
from pyramid.httpexceptions import HTTPFound
from pyramid.response import FileResponse
from pyramid.asset import abspath_from_asset_spec
from pyramid.security import NO_PERMISSION_REQUIRED

from ..lib.utils import _
from ..models import close_dbsession


# =============================================================================
class HomeView(object):
    """Class to manage *Home* pages."""

    # -------------------------------------------------------------------------
    def __init__(self, request):
        """Constructor method."""
        request.add_finished_callback(close_dbsession)
        self._request = request

    # -------------------------------------------------------------------------
    @view_config(route_name='home', renderer='../Templates/home.pt')
    def index(self):
        """Index page."""
        if 'breadcrumbs' in self._request.session:
            del self._request.session['breadcrumbs']

        home = self._request.session.get('home')
        if home == 'projects':
            return HTTPFound(self._request.route_path('project_index'))
        elif home == 'storages':
            return HTTPFound(self._request.route_path('storage_index'))
        elif home == 'site':
            return HTTPFound(self._request.route_path('site_admin'))

        self._request.breadcrumbs.add(_('Home'), 1, 1)
        return {}


# =============================================================================
@view_config(route_name='favicon', permission=NO_PERMISSION_REQUIRED)
def favicon(request):
    """Output the `favicon.ico` file."""
    settings = request.registry.settings
    if settings.get('skin.favicon') and settings.get('skin.static.name'):
        icon = join(abspath_from_asset_spec(settings['skin.static.path']),
                    settings.get('skin.favicon')[1:].partition('/')[2])
    else:
        icon = join(dirname(__file__), '..', 'Static', 'favicon.ico')
    return FileResponse(icon, request=request)


# =============================================================================
@view_config(route_name='robots', permission=NO_PERMISSION_REQUIRED)
def robots(request):
    """Output the `robots.txt` file."""
    robots_txt = join(dirname(__file__), '..', 'Static', 'robots.txt')
    return FileResponse(robots_txt, request=request)
