# $Id: jobs.py 23e2252b8fab 2015/11/29 23:26:16 Patrick $
"""SQLAlchemy-powered model definition for project background jobs."""
# pylint: disable = locally-disabled, super-on-old-class

from logging import getLogger
from time import time
from locale import getdefaultlocale
from lxml import etree
from sqlalchemy import Column, ForeignKey, types
from sqlalchemy.schema import ForeignKeyConstraint, UniqueConstraint
from sqlalchemy.exc import IntegrityError
from sqlalchemy.orm import relationship

from ..lib.utils import _, localizer, normalize_spaces, wrap
from . import LABEL_LEN, DESCRIPTION_LEN
from . import Base, DBSession
from .tasks import LINK_TYPES


LOG = getLogger(__name__)
DEFAULT_TTL = 300
DEFAULT_LOG_TTL = 604800
JOB_FILE_TYPES = ('resource', 'template')
JOB_LOG_STATUS = ('info', 'warning', 'error')
XML_NS = '{http://www.w3.org/XML/1998/namespace}'


# =============================================================================
class Job(Base):
    """SQLAlchemy-powered project background job model."""
    # pylint: disable = locally-disabled, too-many-instance-attributes

    __table_args__ = (
        UniqueConstraint('project_id', 'label'), {'mysql_engine': 'InnoDB'})
    __tablename__ = 'job'

    project_id = Column(
        types.Integer,
        ForeignKey('project.project_id', ondelete='CASCADE'),
        primary_key=True)
    job_id = Column(types.Integer, primary_key=True)
    label = Column(types.String(LABEL_LEN), nullable=False)
    description = Column(types.String(DESCRIPTION_LEN))
    processing_id = Column(types.Integer, nullable=False)
    ttl = Column(types.Integer, default=DEFAULT_TTL)
    log_ttl = Column(types.Integer, default=DEFAULT_LOG_TTL)
    period = Column(types.Integer, default=1)
    task_ko_id = Column(types.Integer)
    task_ko_mode = Column(
        types.Enum(*LINK_TYPES.keys(), name='jobmod_enum'), default='normal')
    task_ok_id = Column(types.Integer)
    task_ok_mode = Column(
        types.Enum(*LINK_TYPES.keys(), name='jobmod_enum'), default='normal')
    sort = Column(types.Integer, default=0)
    stopped = Column(types.Boolean, default=False)
    period_count = Column(types.Integer, default=0)
    start = Column(types.Float)
    lock = Column(types.Boolean, default=False)
    packs = relationship('JobPack')
    log = relationship('JobLog')

    # -------------------------------------------------------------------------
    def __init__(self, project_id, label, description, processing_id, ttl=None,
                 log_ttl=None, period=None, task_ko_id=None, task_ko_mode=None,
                 task_ok_id=None, task_ok_mode=None, sort=None, stopped=False):
        """Constructor method."""
        # pylint: disable = locally-disabled, R0913
        super(Job, self).__init__()
        self.project_id = project_id
        self.label = normalize_spaces(label, LABEL_LEN)
        self.description = normalize_spaces(description, DESCRIPTION_LEN)
        self.processing_id = processing_id
        if ttl:
            self.ttl = int(ttl)
        if log_ttl:
            self.log_ttl = int(log_ttl)
        if period:
            self.period = int(period)
            self.period_count = self.period - 1
        self.task_ko_id = task_ko_id
        self.task_ko_mode = task_ko_mode
        self.task_ok_id = task_ok_id
        self.task_ok_mode = task_ok_mode
        self.sort = sort
        self.stopped = stopped

    # -------------------------------------------------------------------------
    @classmethod
    def load(cls, project_id, processing_dict, pack_dict, task_dict, job_elt):
        """Load a background job from a XML element.

        :param project_id: (string)
            Current project ID.
        :param processing_dict: (dictionary)
            Relationship between XML ID and SQL ID for processings.
        :param pack_dict: (dictionary)
            Relationship between XML ID and SQL ID for packs.
        :param task_dict: (dictionary)
            Relationship between XML ID and SQL ID for tasks.
        :param job_elt: (:class:`lxml.etree.Element` instance)
            Processing XML element.
        :return: (:class:`pyramid.i18n.TranslationString` or integer)
            Error message or integer.
        """
        if job_elt is None:
            return _('nothing to do!')

        label = normalize_spaces(job_elt.findtext('label'), LABEL_LEN)
        job = DBSession.query(cls).filter_by(
            project_id=project_id, label=label).first()
        if job is not None:
            return _('Background job "${l}" already exists.', {'l': label})

        task_ko = job_elt.find('task-ko')
        task_ko = task_ko is not None and \
            (task_dict[task_ko.get('ref')], task_ko.get('mode')) or \
            (None, None)
        task_ok = job_elt.find('task-ok')
        task_ok = task_ok is not None and \
            (task_dict[task_ok.get('ref')], task_ok.get('mode')) or \
            (None, None)
        job = cls(
            project_id, label, job_elt.findtext('description'),
            processing_dict[job_elt.find('processing').get('ref')],
            job_elt.get('ttl'), job_elt.get('log-ttl'), job_elt.get('period'),
            task_ko[0], task_ko[1], task_ok[0], task_ok[1],
            job_elt.xpath('count(preceding-sibling::job)+1'),
            job_elt.get('stopped', False) == 'true')

        # Load packs
        for child in job_elt.findall('packs/pack'):
            job.packs.append(JobPack(pack_dict[child.get('ref')]))

        DBSession.add(job)
        try:
            DBSession.commit()
        except IntegrityError as err:
            DBSession.rollback()
            LOG.error(err)
            return err
        return job.job_id

    # -------------------------------------------------------------------------
    def xml(self):
        """Serialize a background job to a XML representation.

        :return: (:class:`lxml.etree.Element`)
        """
        job_elt = etree.Element('job')
        if self.ttl != DEFAULT_TTL:
            job_elt.set('ttl', str(self.ttl))
        if self.log_ttl != DEFAULT_LOG_TTL:
            job_elt.set('log-ttl', str(self.log_ttl))
        if self.period != 1:
            job_elt.set('period', str(self.period))
        if self.stopped:
            job_elt.set('stopped', 'true')
        etree.SubElement(job_elt, 'label').text = self.label
        if self.description:
            etree.SubElement(job_elt, 'description').text = \
                wrap(self.description, width=66, indent=12)

        # Processing
        etree.SubElement(
            job_elt, 'processing',
            ref='prc%d.%d' % (self.project_id, self.processing_id))

        # Packs
        if self.packs:
            elt = etree.SubElement(job_elt, 'packs')
            for pack in self.packs:
                etree.SubElement(
                    elt, 'pack',
                    ref='pck%d.%d' % (pack.project_id, pack.pack_id))

        # Tasks
        if self.task_ko_id:
            elt = etree.SubElement(
                job_elt, 'task-ko',
                ref='tsk%d.%d' % (self.project_id, self.task_ko_id))
            if self.task_ko_mode != 'normal':
                elt.set('mode', self.task_ko_mode)
        if self.task_ok_id:
            elt = etree.SubElement(
                job_elt, 'task-ok',
                ref='tsk%d.%d' % (self.project_id, self.task_ok_id))
            if self.task_ok_mode != 'normal':
                elt.set('mode', self.task_ok_mode)

        return job_elt

    # -------------------------------------------------------------------------
    def message(self, status, text):
        """Save a message in the database.

        :param status: ('info', 'warning' or 'error')
        :param text: (string or :class:`pyramid.i18n.TranslationString`)
            Message text.
        """
        text = localizer(getdefaultlocale()[0]).translate(text)
        {'warning': LOG.warning, 'error': LOG.error}.get(status, LOG.info)(
            text)
        self.log.append(JobLog(status, text))
        DBSession.commit()


# =============================================================================
class JobPack(Base):
    """SQLAlchemy-powered project background job pack model."""
    # pylint: disable = locally-disabled, R0903

    __tablename__ = 'job_pack'
    __table_args__ = (
        ForeignKeyConstraint(
            ['project_id', 'job_id'], ['job.project_id', 'job.job_id'],
            ondelete='CASCADE'),
        {'mysql_engine': 'InnoDB'})
    project_id = Column(types.Integer, primary_key=True)
    job_id = Column(types.Integer, primary_key=True)
    pack_id = Column(types.Integer, primary_key=True)

    # -------------------------------------------------------------------------
    def __init__(self, pack_id):
        """Constructor method."""
        super(JobPack, self).__init__()
        self.pack_id = pack_id


# =============================================================================
class JobLog(Base):
    """SQLAlchemy-powered project background job log model."""
    # pylint: disable = locally-disabled, R0903

    __tablename__ = 'job_log'
    __table_args__ = (
        ForeignKeyConstraint(
            ['project_id', 'job_id'], ['job.project_id', 'job.job_id'],
            ondelete='CASCADE'),
        {'mysql_engine': 'InnoDB'})
    project_id = Column(types.Integer, primary_key=True)
    job_id = Column(types.Integer, primary_key=True)
    moment = Column(types.Float(), primary_key=True, default=time())
    status = Column(types.Enum(*JOB_LOG_STATUS, name='joblog_status_enum'))
    text = Column(types.Text, nullable=False)

    # -------------------------------------------------------------------------
    def __init__(self, status, text):
        """Constructor method."""
        super(JobLog, self).__init__()
        self.moment = time()
        self.status = status
        self.text = text.strip()
