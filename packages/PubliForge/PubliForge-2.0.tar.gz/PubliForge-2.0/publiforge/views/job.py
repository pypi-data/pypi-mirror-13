# $Id: job.py 97132291b57d 2015/05/16 22:31:25 Patrick $
"""Background job view callables."""

from sqlalchemy import desc
from colander import Mapping, SchemaNode, Integer, Boolean
from colander import String, Length, OneOf

from pyramid.view import view_config
from pyramid.httpexceptions import HTTPNotFound, HTTPFound, HTTPForbidden

from ..lib.utils import _, has_permission, age, duration, normalize_spaces
from ..lib.viewutils import get_action, current_project
from ..lib.packutils import paging_packs
from ..lib.form import Form
from ..lib.widget import Paging, TabSet
from ..models import LABEL_LEN, DESCRIPTION_LEN
from ..models import DBSession, close_dbsession
from ..models.processings import Processing
from ..models.tasks import LINK_TYPES
from ..models.jobs import DEFAULT_TTL, DEFAULT_LOG_TTL, Job, JobLog, JobPack
from ..models.packs import Pack


JOB_SETTINGS_TABS = (_('Description'), _('Packs'), _('Connections'))
TTL_VALUES = (60, 120, 180, 240, 300, 360, 600, 900, 1800, 3600, 7200)
LOG_TTL_VALUES = (
    900, 1800, 3600, 7200, 86400, 172800, 604800, 1209600, 2592000)
PERIOD_VALUES = (1, 2, 3, 4, 5, 10, 20, 30, 60, 120, 240)


# =============================================================================
class JobView(object):
    """Class to manage background jobs."""

    # -------------------------------------------------------------------------
    def __init__(self, request):
        """Constructor method."""
        request.add_finished_callback(close_dbsession)
        self._request = request

    # -------------------------------------------------------------------------
    @view_config(route_name='job_index', renderer='../Templates/job_index.pt')
    def index(self):
        """List current background jobs for a project."""
        # Authorization
        project = current_project(self._request)
        if self._request.session['project']['perm'] != 'leader' \
                and not has_permission(self._request, 'prj_editor'):
            raise HTTPForbidden()

        # Action
        action, items = get_action(self._request)
        if action[0:4] in ('act!', 'stp!'):
            for job_id in items:
                job = DBSession.query(Job).filter_by(
                    project_id=project['project_id'], job_id=int(job_id))\
                    .first()
                if job is not None:
                    job.stopped = action[0:4] == 'stp!'
                    job.lock = 0
                    job.period_count = job.period - 1
            DBSession.commit()
        elif action[0:4] == 'del!':
            for job_id in items:
                DBSession.query(JobLog).filter_by(
                    project_id=project['project_id'], job_id=int(job_id))\
                    .delete()
            DBSession.commit()

        # Background job list
        jobs = DBSession.query(Job).filter_by(
            project_id=project['project_id']).order_by(Job.sort)

        # Breadcrumb trail
        self._request.breadcrumbs.add(_('Background jobs'), 3)

        return {
            'age': age, 'project': project, 'jobs': jobs, 'action': action}

    # -------------------------------------------------------------------------
    @view_config(route_name='job_log', renderer='../Templates/job_log.pt')
    def log(self):
        """Display the background job log."""
        # Authorization
        project = current_project(self._request)
        if self._request.session['project']['perm'] != 'leader' \
                and not has_permission(self._request, 'prj_editor'):
            raise HTTPForbidden()

        # Get job
        job = DBSession.query(Job).filter_by(
            project_id=project['project_id'],
            job_id=int(self._request.matchdict.get('job_id'))).first()
        if job is None:
            raise HTTPNotFound(
                comment=_('This background job does not exist!'))

        # Action
        action = get_action(self._request)[0]
        if action == 'del!':
            DBSession.query(JobLog).filter_by(
                project_id=job.project_id, job_id=job.job_id).delete()
            DBSession.commit()

        # Log
        query = DBSession.query(JobLog).filter_by(
            project_id=job.project_id, job_id=job.job_id).order_by(
                desc(JobLog.moment))
        paging = Paging(self._request, 'job_log', query)

        # Breadcrumb trail
        self._request.breadcrumbs.add(_('Background job log'))

        return {
            'age': age, 'project': project, 'job': job, 'action': action,
            'paging': paging}

    # -------------------------------------------------------------------------
    @view_config(route_name='job_view', renderer='../Templates/job_view.pt')
    def view(self):
        """Show background job settings."""
        project = current_project(self._request)
        job = DBSession.query(Job).filter_by(
            job_id=int(self._request.matchdict.get('job_id'))).first()
        if job is None:
            raise HTTPNotFound()
        tab_set = TabSet(self._request, JOB_SETTINGS_TABS)
        i_editor = project['perm'] == 'leader' \
            or has_permission(self._request, 'prj_editor')

        # Processing
        processing_label = \
            dict(project['processing_labels']).get(job.processing_id)
        if processing_label is None:
            processing_label = DBSession.query(Processing.label).filter_by(
                project_id=job.project_id, processing_id=job.processing_id)\
                .first()
            processing_label = processing_label and processing_label[0] or ''

        # Packs
        packs = [k.pack_id for k in job.packs]
        packs = packs and DBSession.query(Pack)\
            .filter_by(project_id=job.project_id)\
            .filter(Pack.pack_id.in_(packs)).all() or tuple()

        self._request.breadcrumbs.add(
            _('Background job settings'), replace=self._request.route_path(
                'job_edit', project_id=job.project_id, job_id=job.job_id))

        return {
            'duration': duration, 'form': Form(self._request),
            'tab_set': tab_set, 'project': project, 'job': job,
            'i_editor': i_editor, 'processing_label': processing_label,
            'task_ko_label': job.task_ko_id and dict(
                project['task_labels'])[job.task_ko_id],
            'task_ok_label': job.task_ok_id and dict(
                project['task_labels'])[job.task_ok_id],
            'LINK_TYPES': LINK_TYPES, 'packs': packs}

    # -------------------------------------------------------------------------
    @view_config(route_name='job_create', renderer='../Templates/job_edit.pt')
    def create(self):
        """Create a background job."""
        # Permission
        project = current_project(self._request)
        if project['perm'] != 'leader' \
                and not has_permission(self._request, 'prj_editor'):
            raise HTTPForbidden()

        # Environment
        form, tab_set, processings = self._settings_form(project)

        # Action
        action = get_action(self._request)[0]
        if action == 'sav!' and form.validate():
            job = self._create(project['project_id'], form.values)
            if job is not None:
                self._request.breadcrumbs.pop()
                del self._request.session['project']
                del self._request.session['menu']
                return HTTPFound(self._request.route_path(
                    'job_edit', project_id=job.project_id,
                    job_id=job.job_id))

        self._request.breadcrumbs.add(_('Background job creation'))

        return {
            'form': form, 'tab_set': tab_set, 'project': project, 'job': None,
            'processings': processings,
            'ttls': [(k, duration(self._request, k)) for k in TTL_VALUES],
            'log_ttls': [
                (k, duration(self._request, k)) for k in LOG_TTL_VALUES],
            'PERIOD_VALUES': PERIOD_VALUES, 'LINK_TYPES': LINK_TYPES,
            'packs': None, 'action': None, 'paging': None}

    # -------------------------------------------------------------------------
    @view_config(route_name='job_edit', renderer='../Templates/job_edit.pt')
    def edit(self):
        """Edit a job."""
        # Authorization
        project = current_project(self._request)
        if project['perm'] != 'leader' \
                and not has_permission(self._request, 'prj_editor'):
            raise HTTPForbidden()

        # Action
        job = DBSession.query(Job).filter_by(
            project_id=project['project_id'],
            job_id=int(self._request.matchdict.get('job_id'))).first()
        if job is None:
            raise HTTPNotFound()
        paging = None
        action, items = get_action(self._request)
        if action == 'add?' \
           or (not action and 'paging_id' in self._request.GET):
            paging = paging_packs(self._request, project['project_id'])[0]
        elif action[0:4] == 'add!':
            pack_ids = [k.pack_id for k in job.packs]
            for pack_id in items:
                pack_id = int(pack_id)
                if pack_id not in pack_ids:
                    job.packs.append(JobPack(pack_id))
            DBSession.commit()
        elif action[0:4] == 'del!':
            DBSession.query(JobPack).filter_by(
                project_id=job.project_id, job_id=job.job_id,
                pack_id=int(action[4:])).delete()
            DBSession.commit()

        # Environment
        form, tab_set, processings = self._settings_form(project, job)
        packs = [k.pack_id for k in job.packs]
        packs = packs and DBSession.query(Pack)\
            .filter_by(project_id=job.project_id)\
            .filter(Pack.pack_id.in_(packs)).all() or tuple()

        # Save
        view_path = self._request.route_path(
            'job_view', project_id=job.project_id, job_id=job.job_id)
        if action == 'sav!' and form.validate(job):
            DBSession.commit()
            del self._request.session['project']
            del self._request.session['menu']
            return HTTPFound(view_path)
        if form.has_error():
            self._request.session.flash(_('Correct errors.'), 'alert')

        # Breadcrumbs
        self._request.breadcrumbs.add(
            _('Background job settings'), replace=view_path)

        return {
            'form': form, 'tab_set': tab_set, 'project': project, 'job': job,
            'processings': processings,
            'ttls': [(k, duration(self._request, k)) for k in TTL_VALUES],
            'log_ttls': [
                (k, duration(self._request, k)) for k in LOG_TTL_VALUES],
            'PERIOD_VALUES': PERIOD_VALUES, 'LINK_TYPES': LINK_TYPES,
            'packs': packs, 'action': action, 'paging': paging}

    # -------------------------------------------------------------------------
    def _settings_form(self, project, job=None):
        """Return a job settings form.

        :param project: (dictionary)
            Current project dictionary.
        :param job: (:class:`~..models.jobs.Job` instance, optional)
            Current job object.
        :return: (tuple)
             A tuple such as ``(form, tab_set, processings)``
        """
        processings = dict(
            DBSession.query(Processing.processing_id, Processing.label).all())

        schema = SchemaNode(Mapping())
        schema.add(SchemaNode(
            String(), name='label', validator=Length(min=2, max=LABEL_LEN)))
        schema.add(SchemaNode(
            Integer(), name='processing_id',
            validator=OneOf(processings.keys())))
        schema.add(SchemaNode(
            String(), name='description', missing='',
            validator=Length(max=DESCRIPTION_LEN)))
        schema.add(SchemaNode(
            Integer(), name='ttl', validator=OneOf(TTL_VALUES)))
        schema.add(SchemaNode(
            Integer(), name='log_ttl', validator=OneOf(LOG_TTL_VALUES)))
        schema.add(SchemaNode(
            Integer(), name='period', validator=OneOf(PERIOD_VALUES)))
        schema.add(SchemaNode(Boolean(), name='stopped', missing=False))
        schema.add(SchemaNode(
            Integer(), name='task_ko_id', missing=None,
            validator=OneOf(project['task_labels'].keys())))
        schema.add(SchemaNode(
            String(), name='task_ko_mode', missing=None,
            validator=OneOf(LINK_TYPES.keys())))
        schema.add(SchemaNode(
            Integer(), name='task_ok_id', missing=None,
            validator=OneOf(project['task_labels'].keys())))
        schema.add(SchemaNode(
            String(), name='task_ok_mode', missing=None,
            validator=OneOf(LINK_TYPES.keys())))
        defaults = {
            'ttl': DEFAULT_TTL, 'log_ttl': DEFAULT_LOG_TTL,
            'task_ko_mode': 'normal', 'task_ok_mode': 'normal'}

        return (
            Form(self._request, schema=schema, defaults=defaults, obj=job),
            TabSet(self._request, JOB_SETTINGS_TABS), processings)

    # -------------------------------------------------------------------------
    def _create(self, project_id, values):
        """Create a record in ``job`` table.

        :param project_id: (string)
            Project ID.
        :param values: (dictionary)
            Values to record.
        :return:
            (:class:`~..models.tasks.Job` instance)
        """
        # Check unicity
        label = normalize_spaces(values['label'], LABEL_LEN)
        job = DBSession.query(Job).filter_by(
            project_id=project_id, label=label).first()
        if job is not None:
            self._request.session.flash(
                _('This background job already exists.'), 'alert')
            return

        # Create job
        job = Job(
            project_id, label, values['description'], values['processing_id'],
            values['ttl'], values['log_ttl'], values['period'],
            values.get('task_ko_id'), values.get('task_ko_mode'),
            values.get('task_ok_id'), values.get('task_ok_mode'), None,
            values['stopped'])
        DBSession.add(job)
        DBSession.commit()

        return job
