# $Id: __init__.py 85ed05a80aea 2015/09/02 09:18:34 Patrick $
# pylint: disable = locally-disabled, C0103
"""Here are defined database main objects and constants."""

from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import scoped_session, sessionmaker

DBSession = scoped_session(sessionmaker())
Base = declarative_base()

NULL = None
TRUE = True
ID_LEN = 32
LABEL_LEN = 96
DESCRIPTION_LEN = 255
PATH_LEN = 255
VALUE_LEN = 255
PATTERN_LEN = 96
ALL_LANG_LIST = ('en', 'fr', 'es')


# =============================================================================
def close_dbsession(request):
    """Call back function to close database session.

    :param request: (:class:`pyramid.request.Request` instance)
        Current request.
    """
    # pylint: disable = locally-disabled, unused-argument
    try:
        DBSession.close()
    except AttributeError:
        pass
