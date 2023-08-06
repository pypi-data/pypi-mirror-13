# $Id: projects.py 23e2252b8fab 2015/11/29 23:26:16 Patrick $
"""SQLAlchemy-powered model definition for projects."""
# pylint: disable = locally-disabled, super-on-old-class

from datetime import datetime
from lxml import etree
from sqlalchemy import or_, and_, Column, ForeignKey, types
from sqlalchemy.orm import relationship

from ..lib.utils import _, normalize_name, normalize_spaces, wrap
from . import ID_LEN, LABEL_LEN, DESCRIPTION_LEN
from . import Base, DBSession
from .roles import Role, RoleUser
from .processings import Processing, ProcessingVariable
from .packs import Pack, PackVariable
from .tasks import Task, TaskLink, TaskProcessing
from .jobs import Job
from .users import User
from .groups import GROUP_USER, Group


PROJECT_STATUS = {
    'draft': _('Draft'), 'active': _('Active'), 'archived': _('Archived')}
PROJECT_PERMS = {
    'leader': _('Leader'), 'packmaker': _('Pack maker'),
    'packeditor': _('Pack editor'), 'member': _('Member')}
PROJECT_ENTRIES = {
    'all': _('All'), 'tasks': _('Task-oriented'), 'packs': _('Pack-oriented')}
XML_NS = '{http://www.w3.org/XML/1998/namespace}'


# =============================================================================
class Project(Base):
    """SQLAlchemy-powered project model."""

    __tablename__ = 'project'
    __table_args__ = {'mysql_engine': 'InnoDB'}

    project_id = Column(types.Integer, primary_key=True)
    label = Column(types.String(LABEL_LEN), unique=True, nullable=False)
    description = Column(types.String(DESCRIPTION_LEN))
    status = Column(types.Enum(*PROJECT_STATUS.keys(), name='prj_status_enum'),
                    nullable=False, default='active')
    deadline = Column(types.Date)
    roles = relationship('Role')
    processings = relationship('Processing')
    packs = relationship('Pack')
    tasks = relationship('Task')
    jobs = relationship('Job')
    users = relationship('ProjectUser', backref='project')
    groups = relationship('ProjectGroup')

    # -------------------------------------------------------------------------
    def __init__(self, label, description=None, status=None, deadline=None):
        """Constructor method."""
        super(Project, self).__init__()
        self.label = normalize_spaces(label, LABEL_LEN)
        self.description = normalize_spaces(description, DESCRIPTION_LEN)
        self.status = status
        if deadline is not None:
            self.deadline = (
                isinstance(deadline, basestring) and
                datetime.strptime(deadline, '%Y-%m-%d')) or deadline

    # -------------------------------------------------------------------------
    @classmethod
    def load(cls, project_elt, error_if_exists=True):
        """Load a project from a XML element.

        :param project_elt: (:class:`lxml.etree.Element` instance)
            Project XML element.
        :param error_if_exists: (boolean, default=True)
            It returns an error if project already exists.
        :return: (:class:`pyramid.i18n.TranslationString` or ``None``)
            Error message or ``None``.
        """
        # Check if already exists
        label = normalize_spaces(project_elt.findtext('label'), LABEL_LEN)
        project = DBSession.query(cls).filter_by(label=label).first()
        if project is not None:
            if error_if_exists:
                return _('Project "${l}" already exists.', {'l': label})
            return

        # Create project
        project = cls(project_elt.findtext('label'),
                      project_elt.findtext('description'),
                      project_elt.get('status', 'active'),
                      project_elt.findtext('deadline'))
        DBSession.add(project)
        DBSession.commit()

        # Append team
        role_dict = cls._load_team(project, project_elt)

        # Append processings
        processing_dict = {}
        elt = project_elt.find('processings')
        if elt is not None:
            for child in elt.findall('processing'):
                processing_dict[child.get('%sid' % XML_NS)] = \
                    Processing.load(project.project_id, child, False)

        # Append tasks
        task_dict = {}
        elt = project_elt.find('tasks')
        if elt is not None:
            for child in elt.findall('task'):
                task_dict[child.get('%sid' % XML_NS)] = \
                    Task.load(project.project_id, role_dict, child)
                if isinstance(
                        task_dict[child.get('%sid' % XML_NS)], basestring):
                    return task_dict[child.get('%sid' % XML_NS)]
            for child in elt.findall('task'):
                TaskLink.load(project.project_id, task_dict, child)
                TaskProcessing.load(
                    project.project_id, task_dict, processing_dict, child)

        # Append packs
        pack_dict = {}
        elt = project_elt.find('packs')
        if elt is not None:
            for child in elt.findall('pack'):
                pack_dict[child.get('%sid' % XML_NS)] = \
                    Pack.load(
                        project.project_id, role_dict, processing_dict,
                        task_dict, child)
                if isinstance(
                        pack_dict[child.get('%sid' % XML_NS)], basestring):
                    return pack_dict[child.get('%sid' % XML_NS)]

        # Append jobs
        cls._load_jobs(
            project, processing_dict, pack_dict, task_dict, project_elt)

        # Correct variables which point to a processing
        cls._correct_processing_variables(project.project_id, processing_dict)

        DBSession.commit()

    # -------------------------------------------------------------------------
    def xml(self, request):
        """Serialize a project to a XML representation.

        :param request: (:class:`pyramid.request.Request` instance)
            Current request.
        :return: (:class:`lxml.etree.Element`)
        """
        # Header
        project_elt = etree.Element('project')
        project_elt.set('status', self.status)
        etree.SubElement(project_elt, 'label').text = self.label
        if self.description:
            etree.SubElement(project_elt, 'description').text = \
                wrap(self.description, indent=8)
        if self.deadline:
            etree.SubElement(project_elt, 'deadline')\
                .text = self.deadline.isoformat()

        # Roles
        if self.roles:
            group_elt = etree.SubElement(project_elt, 'roles')
            for role in sorted(self.roles, key=lambda k: k.role_id):
                group_elt.append(etree.Comment(u'{0:~^64}'.format(
                    u' Role: %s ' % role.label)))
                group_elt.append(role.xml())

        # Processings
        if self.processings:
            group_elt = etree.SubElement(project_elt, 'processings')
            for processing \
                    in sorted(self.processings, key=lambda k: k.processing_id):
                group_elt.append(etree.Comment(u'{0:~^64}'.format(
                    u' Processing: %s ' % processing.label)))
                processor = request.registry['fbuild'].processor(
                    request, processing.processor)
                group_elt.append(processing.xml(processor))

        # Tasks
        if self.tasks:
            group_elt = etree.SubElement(project_elt, 'tasks')
            for task in sorted(self.tasks, key=lambda k: k.task_id):
                group_elt.append(etree.Comment(u'{0:~^64}'.format(
                    u' Task: %s ' % task.label)))
                group_elt.append(task.xml())

        # Jobs
        if self.jobs:
            group_elt = etree.SubElement(project_elt, 'jobs')
            for job in sorted(self.jobs, key=lambda k: k.sort):
                group_elt.append(etree.Comment(u'{0:~^64}'.format(
                    u' Job: %s ' % job.label)))
                group_elt.append(job.xml())

        # Packs
        if self.packs:
            group_elt = etree.SubElement(project_elt, 'packs')
            for pack in sorted(self.packs, key=lambda k: k.pack_id):
                group_elt.append(etree.Comment(u'{0:~^64}'.format(
                    u' Pack: %s ' % pack.label)))
                group_elt.append(pack.xml())

        # Team
        self._xml_team(project_elt)

        return project_elt

    # -------------------------------------------------------------------------
    @classmethod
    def team_query(cls, project_id):
        """Query to retrieve ID, login and name of each member of the project
        ``project_id``.

        :param project_id: (integer)
            Project ID.
        :return: (:class:`sqlalchemy.orm.query.Query` instance)
        """
        groups = DBSession.query(ProjectGroup.group_id).filter_by(
            project_id=project_id).all()
        query = DBSession.query(User.user_id, User.login, User.name)
        if groups:
            query = query.filter(or_(
                and_(ProjectUser.project_id == project_id,
                     ProjectUser.user_id == User.user_id),
                and_(GROUP_USER.c.group_id.in_(groups),
                     GROUP_USER.c.user_id == User.user_id)))\
                .distinct(User.user_id, User.login, User.name)
        else:
            query = query.join(ProjectUser)\
                .filter(ProjectUser.project_id == project_id)
        query = query.filter(User.status == 'active')

        return query

    # -------------------------------------------------------------------------
    @classmethod
    def _load_team(cls, project, project_elt):
        """Load users and groups for project.

        :param project: (:class:`Project` instance)
            SQLAlchemy-powered Project object.
        :param roles: (dictionary)
            Relationship between XML ID and SQL ID for roles.
        :param project_elt: (:class:`lxml.etree.Element` instance)
            Project element.
        :return: (dictionary)
            Relationship between XML ID and SQL ID for roles.
        """
        # Roles
        roles = {}
        elt = project_elt.find('roles')
        if elt is not None:
            for child in elt.findall('role'):
                roles[child.get('%sid' % XML_NS)] = \
                    Role.load(project.project_id, child)

        # Users
        done = []
        for item in project_elt.findall('members/member'):
            login = normalize_name(item.text)[0:ID_LEN]
            if login not in done:
                user = DBSession.query(User).filter_by(login=login).first()
                if user is not None:
                    project.users.append(ProjectUser(
                        project.project_id, user.user_id, item.get('in-menu'),
                        item.get('permission', 'member'), item.get('entries')))
                    if item.get('roles'):
                        DBSession.flush()
                        for role in item.get('roles').split():
                            DBSession.add(RoleUser(
                                project.project_id, roles[role], user.user_id))
                done.append(login)

        # Groups
        done = []
        for item in project_elt.findall('members/member-group'):
            group_id = normalize_name(item.text)[0:ID_LEN]
            if group_id not in done:
                done.append(group_id)
                group = DBSession.query(Group).filter_by(
                    group_id=group_id).first()
                if group is not None:
                    project.groups.append(
                        ProjectGroup(
                            project.project_id, group.group_id,
                            item.get('permission')))

        return roles

    # -------------------------------------------------------------------------
    @classmethod
    def _load_jobs(
            cls, project, processing_dict, pack_dict, task_dict, project_elt):
        """Load background jobs for project.

        :param project: (:class:`Project` instance)
            SQLAlchemy-powered Project object.
        :param processing_dict: (dictionary)
            Relationship between XML ID and SQL ID for processings.
        :param pack_dict: (dictionary)
            Relationship between XML ID and SQL ID for packs.
        :param task_dict: (dictionary)
            Relationship between XML ID and SQL ID for tasks.
        :param project_elt: (:class:`lxml.etree.Element` instance)
            Project element.
        """
        jobs_elt = project_elt.find('jobs')
        if jobs_elt is not None:
            for job_elt in jobs_elt.findall('job'):
                Job.load(project.project_id, processing_dict, pack_dict,
                         task_dict, job_elt)

    # -------------------------------------------------------------------------
    def _xml_team(self, project_elt):
        """Serialize users and groups to a XML representation.

        :param project_elt: (:class:`lxml.etree.Element` instance)
            Project element.
        """
        if not self.users and not self.groups:
            return
        project_elt.append(etree.Comment(u'{0:~^66}'.format(' Team ')))

        # Users
        group_elt = etree.SubElement(project_elt, 'members')
        for user in self.users:
            elt = etree.SubElement(group_elt, 'member')
            elt.text = user.user.login
            if user.perm != 'member':
                elt.set('permission', user.perm or 'none')
            if user.in_menu:
                elt.set('in-menu', 'true')
            if user.entries != 'all':
                elt.set('entries', user.entries)
            roles = DBSession.query(RoleUser.role_id).filter_by(
                project_id=self.project_id, user_id=user.user_id).all()
            if roles:
                elt.set('roles', ' '.join([
                    'rol%d.%d' % (self.project_id, k[0]) for k in roles]))

        # Groups
        for group in self.groups:
            elt = etree.SubElement(group_elt, 'member-group')
            elt.text = group.group_id
            if group.perm != 'member':
                elt.set('permission', group.perm)

    # -------------------------------------------------------------------------
    @classmethod
    def _correct_processing_variables(cls, project_id, processing_dict):
        """Correct values of processing type variables according to
        ``processings`` dictionary.

        :param project_id: (integer)
            Project ID.
        :param processing_dict: (dictionary)
            Relationship between XML ID and SQL ID for processings.
        """
        # Correct default values for processing
        for var in DBSession.query(ProcessingVariable)\
                .filter_by(project_id=project_id):
            if var.name.startswith('processing') \
               and var.default in processing_dict:
                var.default = 'prc%d.%d' % (
                    project_id, processing_dict[var.default])

        # Correct default values for pack
        for var in DBSession.query(PackVariable)\
                .filter_by(project_id=project_id):
            if var.name.startswith('processing') \
               and var.value in processing_dict:
                var.value = 'prc%d.%d' % (
                    project_id, processing_dict[var.value])

        DBSession.commit()


# =============================================================================
class ProjectUser(Base):
    """SQLAlchemy-powered association table between ``Project`` and
    ``User``."""
    # pylint: disable = locally-disabled, R0903

    __tablename__ = 'project_user'
    __table_args__ = {'mysql_engine': 'InnoDB'}

    project_id = Column(
        types.Integer, ForeignKey('project.project_id', ondelete='CASCADE'),
        primary_key=True)
    user_id = Column(
        types.Integer, ForeignKey('user.user_id', ondelete='CASCADE'),
        primary_key=True)
    in_menu = Column(types.Boolean, default=False)
    perm = Column(
        types.Enum(*PROJECT_PERMS.keys() + ['none'], name='prj_perms_enum'))
    entries = Column(
        types.Enum(*PROJECT_ENTRIES.keys(), name='prj_entries_enum'),
        default='all')
    user = relationship('User')

    # -------------------------------------------------------------------------
    def __init__(self, project_id, user_id, in_menu=False, perm='member',
                 entries=None):
        """Constructor method."""
        super(ProjectUser, self).__init__()
        self.project_id = project_id
        self.user_id = user_id
        self.in_menu = bool(in_menu)
        if perm != 'none':
            self.perm = perm
        self.entries = entries


# =============================================================================
class ProjectGroup(Base):
    """SQLAlchemy-powered association table between ``Project`` and
    ``Group``."""
    # pylint: disable = locally-disabled, R0903

    __tablename__ = 'project_group'
    __table_args__ = {'mysql_engine': 'InnoDB'}

    project_id = Column(
        types.Integer, ForeignKey('project.project_id', ondelete='CASCADE'),
        primary_key=True)
    group_id = Column(
        types.String(ID_LEN),
        ForeignKey('group.group_id', ondelete='CASCADE'), primary_key=True)
    perm = Column(
        types.Enum(*PROJECT_PERMS.keys(), name='prj_perms_enum'),
        default='member')

    # -------------------------------------------------------------------------
    def __init__(self, project_id, group_id, perm=None):
        """Constructor method."""
        super(ProjectGroup, self).__init__()
        self.project_id = project_id
        self.group_id = group_id.strip()[0:ID_LEN]
        self.perm = perm
