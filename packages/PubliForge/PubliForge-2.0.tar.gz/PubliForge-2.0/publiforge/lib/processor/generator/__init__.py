# $Id: __init__.py aa4d82d217d6 2015/12/12 18:36:44 Patrick $
"""This module generate something from nothing."""

from os.path import join, exists, dirname, basename, splitext
from ConfigParser import ConfigParser
from imp import load_source
from beaker.cache import CacheManager
from beaker.util import parse_cache_config_options

from ...utils import _, config_get, decrypt
from ...handler import HandlerManager
from ....models import DBSession
from ....models.storages import Storage
from .. import bin_directory


# =============================================================================
class Processor(object):
    """Main class for generator processor."""

    # -------------------------------------------------------------------------
    def __init__(self, build):
        """Constructor method.

        :param build: (:class:`~.lib.build.agent.AgentBuild`)
            Main Build object.
        """
        # Attributes
        self.build = build
        self._handler_manager = None
        self._handlers = {}

        # Configuration
        name = join(build.path, 'Processor', 'generator.ini')
        if not exists(name):
            build.stopped(_('File "generator.ini" is missing.'))
            return
        self._config = ConfigParser({
            'here': dirname(name),
            'bin': bin_directory(),
            'processor': join(build.path, 'Processor'),
            'stgpath': build.data_path,
            'lang': build.context['lang']})
        self._config.read(name)

    # -------------------------------------------------------------------------
    def start(self):
        """Start the processor."""
        if self.build.stopped():
            return

        # Load script
        filename = self.config('Generation', 'process')
        if not filename:
            self.build.stopped(_('Option [Generation]/process is missing.'))
            return
        if not exists(filename):
            self.build.stopped(
                _('Unknown file "${n}".', {'n': basename(filename)}))
            return
        module = load_source(splitext(basename(filename))[0], filename)

        # Execute script
        module.main(self)

    # -------------------------------------------------------------------------
    def message(self, text):
        """Add a message in ``build.result['values']``.

        :param text: (string or :class:`pyramid.i18n.TranslationString`)
            Message text.
        """
        if 'values' not in self.build.result:
            self.build.result['values'] = []
        self.build.result['values'].append(self.build.translate(text))

    # -------------------------------------------------------------------------
    def storage_handler(self, storage_id, storage=None):
        """Update environment for storage ``storage_id`` with handler and user
        information and return the current storage handler.

        :param storage_id: (string)
            Storage ID.
        :param storage: (:class:`~.models.storages.Storage` instance,
            optional).
        :return: (tuple or ``None``)
            A tuple such as
            ``(storage_handler, (vcs_user_id, vcs_password, user_name))``.
        """
        if not self.build.context['local']:
            self.build.stopped(
                _('This processor does not work on a pure agent.'))
            return

        # Get handler manager
        if self._handler_manager is None:
            cache_manager = CacheManager(
                **parse_cache_config_options(self.build.settings))
            self._handler_manager = HandlerManager(
                self.build.settings, cache_manager)

        # Already used?
        if storage_id in self._handlers and \
           storage_id in self._handler_manager.currently_managed():
            return self._handlers[storage_id]

        # Create
        if storage is None:
            storage = DBSession.query(Storage).filter_by(
                storage_id=storage_id).first()
        if storage is None:
            self.build.stopped(_('Unknown storage "${n}".', {'n': storage_id}))
            return
        self._handlers[storage_id] = (
            self._handler_manager.get_handler(storage_id, storage),
            (storage.vcs_user,
             decrypt(storage.vcs_password,
                     self.build.settings.get('encryption', '-')),
             self.build.context['name']))
        return self._handlers[storage_id]

    # -------------------------------------------------------------------------
    def config(self, section, option, default=None):
        """Retrieve a value from a configuration object.

        :param section: (string)
            Section name.
        :param option: (string)
            Option name.
        :param default: (string, optional)
            Default value
        :return: (string)
            Read value or default value.
        """
        return config_get(self._config, section, option, default)
