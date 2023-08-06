#!/usr/bin/env python
# $Id: pfscheduler.py 4e76e94f3c7a 2015/12/21 16:29:59 Patrick $
"""Console script to schedule jobs."""

from logging import getLogger
from argparse import ArgumentParser
from os import walk
from os import makedirs
from os.path import exists, join, normpath, relpath
from time import time
from datetime import datetime
from locale import getdefaultlocale
from getpass import getuser
from sqlalchemy import engine_from_config
from beaker.cache import CacheManager
from beaker.util import parse_cache_config_options

from pyramid.paster import get_appsettings

from ..lib.utils import _, localizer, setup_logging, camel_case, copy_content
from ..lib.utils import decrypt, EXCLUDED_FILES
from ..lib.xml import load
from ..lib.handler import HandlerManager
from ..lib.packutils import operator4task
from ..lib.build.agent import AgentBuildManager
from ..models import DBSession, Base
from ..models.users import User
from ..models.roles import Role
from ..models.storages import Storage
from ..models.processings import Processing
from ..models.packs import Pack, PackFile, PackEvent
from ..models.tasks import Task
from ..models.jobs import Job, JobLog


__credits__ = '(c) Prismallia http://www.prismallia.fr, 2010-2015'


LOG = getLogger(__name__)
DEFAULT_SETTINGS_NAME = 'PubliForge'


# =============================================================================
def main():
    """Main function."""
    # Parse arguments
    parser = ArgumentParser(description='Schedule jobs.')
    parser.add_argument(
        'conf_uri', help='URI of configuration (e.g. pfinstance.ini#foo)')
    parser.add_argument(
        'job', nargs='*', help='optional list of jobs to execute')
    parser.add_argument(
        '--list-jobs', dest='list_jobs', help='list current jobs',
        action='store_true')
    parser.add_argument(
        '--stop', dest='stop', help='stop jobs', action='store_true')
    parser.add_argument(
        '--start', dest='start', help='start jobs', action='store_true')
    parser.add_argument(
        '--log-level', dest='log_level', help='log level', default='ERROR',
        choices=('DEBUG', 'INFO', 'WARNING', 'ERROR', 'CRITICAL'))
    parser.add_argument('--log-file', dest='log_file', help='log file')
    args = parser.parse_args()
    if not exists(args.conf_uri.partition('#')[0]):
        parser.print_usage()
        return
    setup_logging(args.log_level, args.log_file)

    # Schedule
    Scheduler(args).start()


# =============================================================================
class Scheduler(object):
    """Class to execute all pending jobs."""

    # -------------------------------------------------------------------------
    def __init__(self, args):
        """Constructor method."""
        self._args = args
        self._build_manager = None

        # Read settings
        self._settings = get_appsettings(args.conf_uri)
        if len(self._settings) < 3:
            try:
                self._settings = get_appsettings(
                    args.conf_uri, DEFAULT_SETTINGS_NAME)
            except LookupError:
                pass
        if 'sqlalchemy.url' not in self._settings or \
           not self._settings.get('processor.roots') or \
           not self._settings.get('processor.list'):
            LOG.critical(self._translate(_(
                'Incorrect configuration file "${f}".', {'f': args.conf_uri})))
            self._settings = None

    # -------------------------------------------------------------------------
    def start(self):
        """Schedule."""
        if self._settings is None:
            return

        # Initialize SqlAlchemy session
        dbengine = engine_from_config(self._settings, 'sqlalchemy.')
        DBSession.configure(bind=dbengine)
        Base.metadata.bind = dbengine

        # List jobs
        if self._args.list_jobs:
            self._list_jobs()
            DBSession.close()
            return

        # Stop or start jobs
        if self._args.stop or self._args.start:
            self._stop_start_jobs()
            DBSession.close()
            return

        # Get build manager
        self._settings['build.reset'] = 'false'
        self._build_manager = AgentBuildManager(self._settings)
        self._build_manager.processor_list()

        # Context
        context = {
            'user_id': 0, 'login': getuser(), 'name': getuser(),
            'lang': getdefaultlocale()[0], 'local': True, 'job': None}

        # Browse jobs
        # pylint: disable = locally-disabled, too-many-boolean-expressions
        processors = {}
        for job in DBSession.query(Job).order_by(Job.project_id, Job.sort):
            # Check job
            DBSession.query(JobLog)\
                .filter_by(project_id=job.project_id, job_id=job.job_id)\
                .filter(JobLog.moment + job.log_ttl < time()).delete()
            DBSession.flush()
            job.period_count = job.period_count + 1 \
                if job.period_count < job.period - 1 else 0
            job_id = 'job%d.%d' % (job.project_id, job.job_id)
            if (self._args.job and job_id not in self._args.job) or \
               job.stopped or (job.lock and job.start + job.ttl > time()) or \
               job.period_count > 0:
                DBSession.commit()
                continue

            # Start builds
            done = False
            for pack in job.packs:
                self._start_build(context, processors, job, pack)
                done = True
            if not done:
                self._start_build(context, processors, job)
            DBSession.commit()

        DBSession.close()

    # -------------------------------------------------------------------------
    def _start_build(self, context, processors, job, pack=None):
        """Start au build on a pack or from nothing.

        :param context: (dictionary)
            Context environment for build.
        :param processors: (dictionary)
            Already got processors.
        :param job: (:class:`~.models.jobs.Job` instance)
            Current job
        :param pack: (:class:`~.models.projects.ProjectPack`, optional)
            Pack object.
        """
        LOG.info('%s job%d.%d', '-' * 60, job.project_id, job.job_id)
        # Pack
        if pack is not None:
            pack = DBSession.query(Pack).filter_by(
                project_id=job.project_id, pack_id=pack.pack_id).first()
            if pack is None:
                job.message('error', _('Nothing to do!'))
                return

        # Processing
        processing = DBSession.query(Processing).filter_by(
            project_id=job.project_id, processing_id=job.processing_id).first()
        if processing is None:
            job.message(
                'error',
                _('Unknown processing "${p}"', {'p': job.processing_id}))
            self._move2task(job, pack, True)
            return
        if not self._update_processors(job, processors, processing):
            self._move2task(job, pack, True)
            return

        # Processing dictionary
        processing_dict = {
            'label': processing.label,
            'processor_id': processing.processor,
            'variables': self._variables2dict(processing, processors, pack),
            'resources': self._files2list(job, processing, 'resource'),
            'templates': self._files2list(job, processing, 'template'),
            'output': processing.output or '',
            'add2pack': processing.add2pack or ''}
        if processing_dict['variables'] is None:
            self._move2task(job, pack, True)
            return
        if pack is not None and processing_dict['output'] and pack.outputs:
            processing_dict['output'] = dict(
                [(k.processing_id, k.path) for k in pack.outputs]).get(
                    processing.processing_id, processing.output)
        if '%(user)s' in processing_dict['output']:
            processing_dict['output'] = processing_dict['output'].replace(
                '%(user)s', camel_case(context['login']))

        # Pack dictionary
        if pack is None:
            pack_dict = {
                'project_id': job.project_id, 'recursive': False,
                'files': [], 'resources': [], 'templates': []}
        else:
            pack_dict = {
                'project_id': pack.project_id, 'pack_id': pack.pack_id,
                'label': pack.label, 'recursive': pack.recursive,
                'files': self._files2list(job, pack, 'file'),
                'resources': self._files2list(job, pack, 'resource'),
                'templates': self._files2list(job, pack, 'template')}

        # Start build
        context['job'] = job
        job.lock = True
        job.start = time()
        DBSession.commit()
        build_id = 'job%d-%d%s' % (
            job.project_id, job.job_id, pack and '-%s' % pack.pack_id or '')
        build = self._build_manager.start_build(
            build_id, context, processing_dict, pack_dict)

        # Retrieve result
        job.lock = False
        context['job'] = None
        if not self._result2joblog(job, build) or \
           not self._output2storage(job, pack, build):
            self._move2task(job, pack, True)
            return
        self._move2task(job, pack)

    # -------------------------------------------------------------------------
    def _list_jobs(self):
        """List current jobs.

        :param jobs: (list)
            List of current jobs.
        """
        print '=' * 80
        print u'{0:^80}'.format(self._translate(_('Background job list')))
        print '=' * 80
        for job in DBSession.query(Job).order_by(Job.project_id, Job.sort):
            print u'[{0:<8} {1:>3}] {2:}'.format(
                'job%d.%d' % (job.project_id, job.job_id),
                job.stopped and 'Off' or 'On', job.label)

    # -------------------------------------------------------------------------
    def _stop_start_jobs(self):
        """Stop/start jobs.

        :param jobs: (list)
            List of current jobs.
        """
        for job in DBSession.query(Job).order_by(Job.project_id, Job.sort):
            job_id = 'job%d.%d' % (job.project_id, job.job_id)
            if not self._args.job or job_id in self._args.job:
                job.stopped = self._args.stop
                job.lock = False
                job.period_count = job.period - 1
                label = "%s (job%d.%d)" % (
                    job.label, job.project_id, job.job_id)
                print self._translate(
                    job.stopped and _('"${j}" stopped', {'j': label}) or
                    _('"${j}" started', {'j': label}))
        DBSession.commit()

    # -------------------------------------------------------------------------
    def _update_processors(self, job, processors, processing):
        """Update the processor list with the XML needed for the job.

        :param job: (:class:`~.models.jobs.Job` instance)
            Current job.
        :param processors: (dictionary)
            Already got processors.
        :param processing: (:class:`~.models.processings.Processing` instance)
            Processing for the job ``job``.
        :return: (boolean)
        """
        if processing.processor in processors:
            return True
        processor = self._build_manager.processor_path(processing.processor)
        if processor is None:
            job.message(
                'error',
                _('Unknown processor ${p}.', {'p': processing.processor}))
            return False
        processor = load(
            join(processor, 'processor.xml'),
            data=self._build_manager.processor_xml(processing.processor))
        if isinstance(processor, basestring):
            job.message('error', processor)
            return False
        processors[processing.processor] = processor
        return True

    # -------------------------------------------------------------------------
    @classmethod
    def _variables2dict(cls, processing, processors, pack):
        """Read variable definitions in processor tree and update them with
        job variables.

        :param processing: (:class:`~.models.processings.Processing` instance)
            Processing for the current job.
        :param processors: (dictionary)
            Processor dictionary.
        :param pack: (:class:`~.models.packs.Pack` instance)
            Pack to process.
        :return: (dictionary)
            Variable dictionary.
        """
        variables = {}
        defaults = dict([(k.name, k.default) for k in processing.variables])
        values = {}
        if pack is not None:
            values = dict([(k.name, k.value) for k in pack.variables
                           if k.processing_id == processing.processing_id])

        # pylint: disable = locally-disabled, redefined-variable-type
        for var in processors[processing.processor].findall(
                'processor/variables/group/var'):
            name = var.get('name')
            value = values[name] if name in values \
                else (defaults[name] if name in defaults and
                      defaults[name] is not None
                      else var.findtext('default', ''))
            if var.get('type') == 'boolean':
                value = bool(value == 'true')
            elif var.get('type') == 'integer':
                value = int(value)
            elif var.get('type') == 'select':
                value = int(value) if value.isdigit() else value
            variables[name] = value

        return variables

    # -------------------------------------------------------------------------
    def _files2list(self, job, record, file_type):
        """Save set of files in a list.

        :param job: (:class:`~.models.jobs.Job` instance)
            Current job
        :param record: (:class:`~.models.processings.Processing`
            or :class:`~.models.projects.ProjectPack` instance).
        :param file_type: ('file', 'resource' or 'template')
            File type.
        """
        file_set = []
        items = [k for k in record.files if k.file_type == file_type]
        if len(items) == 0:
            return file_set

        storage_root = self._settings['storage.root']
        for item in sorted(items, key=lambda k: k.sort):
            if not exists(join(storage_root, item.path)):
                job.message(
                    'error', _('"${n}" does not exist.', {'n': item.path}))
                return
            if file_type not in ('file', 'resource'):
                file_set.append((item.path, item.target))
            else:
                file_set.append(item.path)

        return file_set

    # -------------------------------------------------------------------------
    @classmethod
    def _result2joblog(cls, job, build):
        """Transfer result to job log table.

        :param job: (:class:`~.models.jobs.Job` instance)
            Current Job object.
        :param build: (:class:`~.lib.build.agent.Build` instance)
            Current build object.
        :return: (boolean)
        """
        warning = False
        for log in build.result['log']:
            if log[1] in ('a_error', 'a_fatal'):
                messages = [
                    '[%-7s] %s' % (k[1], k[3]) for k in build.result['log']]
                job.message('error', '\n'.join(messages))
                return False
            elif log[1] == 'a_warn':
                warning = True

        # Transfer result
        messages = []
        for text in build.result.get('values', ''):
            messages.append(build.translate(text))
        if warning:
            messages.append(build.translate(
                _('Successfully completed but with warnings')))
            messages.append('-' * 80)
            messages += [
                '[%-7s] %s' % (k[1], k[3]) for k in build.result['log']]

        # Display files
        if build.processing['output']:
            for name in build.result.get('files', ''):
                messages.append(build.translate(_(
                    'File = ${n}',
                    {'n': join(build.processing['output'], name)})))

        if messages:
            job.message(warning and 'warning' or 'info', '\n'.join(messages))
        return True

    # -------------------------------------------------------------------------
    def _output2storage(self, job, pack, build):
        """Transfer output files to storage.

        :param job: (:class:`~.models.jobs.Job` instance)
            Current Job object.
        :param pack: (:class:`~.models.packs.Pack` instance)
            Pack to process.
        :param build: (:class:`~.lib.build.agent.Build` instance)
            Current build object.
        :return: (boolean)
        """
        if not build.processing['output']:
            return

        # Find target
        storage_root = normpath(self._settings['storage.root'])
        target = normpath(join(storage_root, build.processing['output']))
        if not target.startswith(storage_root):
            job.message('error', _('Access was denied to this resource.'))
            return False
        storage_id = build.processing['output'].partition('/')[0]
        if not exists(join(storage_root, storage_id)):
            job.message(
                'error', _('"${n}" does not exist.', {'n': storage_id}))
            return False
        if not exists(target):
            makedirs(target)

        # Copy and add files
        copy_content(join(build.path, 'Output'), target)
        storage = DBSession.query(Storage).filter_by(
            storage_id=storage_id).first()
        if storage.vcs_engine == 'none':
            return True
        cache_manager = CacheManager(
            **parse_cache_config_options(self._settings))
        handler_manager = HandlerManager(self._settings, cache_manager)
        handler = handler_manager.get_handler(storage_id, storage)
        handler.add(
            (storage.vcs_user,
             decrypt(storage.vcs_password,
                     self._settings.get('encryption', '-')),
             build.context['name']),
            build.processing['output'].partition('/')[2],
            build.processing['label'])

        # Add to pack
        if build.processing['add2pack']:
            self._result2pack(pack, build)

        return True

    # -------------------------------------------------------------------------
    @classmethod
    def _result2pack(cls, pack, build):
        """Add result to pack.

        :param pack: (:class:`~.models.packs.Pack` instance)
            Pack to process.
        :param build: (:class:`~.lib.build.agent.Build` instance)
            Current build object.
        """
        if pack is None:
            return

        # File list
        packing = {}
        mode = build.processing['add2pack']
        if mode[:6] == 'result' or mode == 'smart':
            packing[mode == 'smart' and 'file' or mode[7:-1]] = \
                sorted(build.result.get('files'))
        if mode[:6] == 'output' or mode == 'smart':
            done = mode == 'smart' and set(build.result.get('files')) or ()
            mode = mode == 'smart' and 'resource' or mode[7:-1]
            packing[mode] = []
            output = join(build.path, 'Output')
            for path, name, files in walk(output):
                for name in sorted(files):
                    if name not in EXCLUDED_FILES and '~' not in name \
                            and relpath(join(path, name), output) not in done:
                        packing[mode].append(relpath(join(path, name), output))

        # Add to database
        for file_type in packing:
            done = set([
                k.path for k in pack.files if k.file_type == file_type])
            for name in packing[file_type]:
                name = join(build.processing['output'], name)
                if name not in done:
                    pack.files.append(PackFile(file_type, name))
        pack.updated = datetime.now()
        pack.update_sort()

    # -------------------------------------------------------------------------
    def _move2task(self, job, pack, error=False):
        """According to ``error``, move managed pack to new task.

        :param job: (:class:`~.models.jobs.Job` instance)
            Current Job object.
        :param build: (:class:`~.lib.build.agent.Build` instance)
            Current build object.
        :param pack: (:class:`~.models.packs.Pack` instance)
            Pack to process.
        :param error: (boolean, default=False)
            ``True`` if error.
        """
        task_id = job.task_ko_id if error else job.task_ok_id
        link_type = job.task_ko_mode if error else job.task_ok_mode
        if pack is None or task_id is None:
            return

        # Find the new operator
        task_id, operator_type, operator_id = operator4task(
            pack, link_type, task_id)

        # Find the new task
        task = DBSession.query(Task).filter_by(
            project_id=job.project_id, task_id=task_id).first()
        if task is None:
            return
        if task.operator_type == 'auto' and task.processings:
            job.message('error',
                        _('A background job cannot launch an automatic task.'))
            return

        # Move pack to task
        pack.task_id = task.task_id
        pack.operator_type = operator_type is not None and operator_type \
            or task.operator_type
        pack.operator_id = operator_type is not None and operator_id \
            or task.operator_id

        # Add event
        if pack.operator_type == 'role':
            label = DBSession.query(Role.label).filter_by(
                role_id=pack.operator_id).first()
            label = self._translate(
                _('[Role] ${l}', {'l': label and label[0] or ''}))
        elif pack.operator_type == 'user':
            label = DBSession.query(User.name).filter_by(
                user_id=pack.operator_id).first()
            label = label and label[0] or ''
        else:
            label = self._translate(_('[Automatic]'))
        event = PackEvent(
            pack.project_id, pack.pack_id, pack.task_id,
            task.label, pack.operator_type, pack.operator_id, label)
        DBSession.add(event)
        DBSession.commit()

    # -------------------------------------------------------------------------
    @classmethod
    def _translate(cls, text):
        """Return ``text`` translated.

        :param text: (string)
            Text to translate.
        """
        return localizer(getdefaultlocale()[0]).translate(text)


# =============================================================================
if __name__ == '__main__':
    main()
