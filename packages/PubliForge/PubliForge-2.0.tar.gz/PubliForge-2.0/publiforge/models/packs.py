# $Id: packs.py 8aad2a4a050d 2016/01/03 10:16:12 Patrick $
"""SQLAlchemy-powered model definition for project tasks."""
# pylint: disable = locally-disabled, super-on-old-class

from logging import getLogger
from datetime import datetime
from os.path import join, exists
from sqlalchemy import Column, ForeignKey, types
from sqlalchemy.schema import ForeignKeyConstraint, UniqueConstraint
from sqlalchemy.orm import relationship
from sqlalchemy.exc import IntegrityError
from lxml import etree

from ..lib.utils import _, normalize_spaces, export_file_set, wrap
from . import ID_LEN, LABEL_LEN, DESCRIPTION_LEN, PATH_LEN, VALUE_LEN
from . import Base, DBSession
from .users import User
from .tasks import OPERATOR_TYPES


LOG = getLogger(__name__)
PCK_FILE_TYPES = ('file', 'resource', 'template')
FILE_TYPE_MARKS = {'file': '', 'resource': _('[R]'), 'template': _('[T]')}
XML_NS = '{http://www.w3.org/XML/1998/namespace}'


# =============================================================================
class Pack(Base):
    """SQLAlchemy-powered project pack model."""
    # pylint: disable = locally-disabled, too-many-instance-attributes

    __tablename__ = 'pack'
    __table_args__ = (
        UniqueConstraint('project_id', 'label'),
        ForeignKeyConstraint(
            ['project_id', 'task_id'],
            ['task.project_id', 'task.task_id']),
        {'mysql_engine': 'InnoDB'})

    project_id = Column(
        types.Integer,
        ForeignKey('project.project_id', ondelete='CASCADE'),
        primary_key=True)
    pack_id = Column(types.Integer, primary_key=True)
    label = Column(types.String(LABEL_LEN), nullable=False)
    description = Column(types.String(DESCRIPTION_LEN))
    recursive = Column(types.Boolean, default=False)
    note = Column(types.Text)
    task_id = Column(types.Integer)
    operator_type = Column(
        types.Enum(*OPERATOR_TYPES, name='operatortype_enum'))
    operator_id = Column(types.Integer, index=True)
    updated = Column(types.DateTime, onupdate=datetime.now)
    created = Column(types.DateTime, default=datetime.now)
    files = relationship('PackFile')
    variables = relationship('PackVariable')
    outputs = relationship('PackOutput')
    events = relationship('PackEvent')

    # -------------------------------------------------------------------------
    def __init__(self, project_id, label, description=None, recursive=False,
                 note=None, pack_id=None, created=None, updated=None):
        """Constructor method."""
        # pylint: disable = locally-disabled, R0913
        super(Pack, self).__init__()
        self.project_id = project_id
        self.pack_id = pack_id
        self.label = normalize_spaces(label, LABEL_LEN)
        self.description = normalize_spaces(description, DESCRIPTION_LEN)
        self.recursive = bool(recursive)
        self.note = note and note.strip() or None
        self.created = created is None and datetime.now() \
            or datetime.strptime(created, '%Y-%m-%dT%H:%M:%S')
        self.updated = updated is None and self.created \
            or datetime.strptime(updated, '%Y-%m-%dT%H:%M:%S')

    # -------------------------------------------------------------------------
    @classmethod  # noqa
    def load(cls, project_id, role_dict, processing_dict, task_dict, pack_elt,
             storage_root=None, pack_id=None):
        """Load a pack from a XML element.

        :param project_id: (integer)
            Project ID.
        :param role_dict: (dictionary)
            Relationship between XML ID and SQL ID for roles.
        :param processing_dict: (dictionary)
            Relationship between XML ID and SQL ID for processings.
        :param task_dict: (dictionary)
            Relationship between XML ID and SQL ID for tasks.
        :param pack_elt: (:class:`lxml.etree.Element` instance)
            Pack XML element.
        :param storage_root: (string, optional)
            Full path to storage root directory. If ``None``, files are not
            checked.
        :param pack_id: (integer, optional)
            Forced pack ID.
        :return: (:class:`pyramid.i18n.TranslationString` or :class:`Pack`)
            Error message or new Pack object.
        """
        # pylint: disable = locally-disabled, R0913, too-many-branches
        # Check if already exists
        ref = normalize_spaces(pack_elt.findtext('label'), LABEL_LEN)
        pack = DBSession.query(cls).filter_by(
            project_id=project_id, label=ref).first()
        if pack is not None:
            return _('Pack "${l}" already exists.', {'l': ref})

        # User cache
        users = {}

        def _operator_id(operator_type, operator_id):
            """Return database ID."""
            if operator_type == 'user':
                if operator_id and operator_id not in users:
                    user = DBSession.query(User).filter_by(
                        login=operator_id).first()
                    if user is not None:
                        users[operator_id] = user.user_id
                operator_id = users.get(operator_id)
            elif operator_type == 'role':
                operator_id = role_dict.get(operator_id)
            return operator_id or None

        # Create pack with its files, variables and history
        pack = cls(
            project_id, pack_elt.findtext('label'),
            pack_elt.findtext('description'), pack_elt.get('recursive'),
            pack_elt.findtext('note'), pack_id,
            pack_elt.get('created'), pack_elt.get('updated'))
        operator = [None, None]  # operator_type, operator_id
        for child in pack_elt.iterdescendants(tag=etree.Element):
            if child.tag in PCK_FILE_TYPES:
                if storage_root is None \
                        or exists(join(storage_root, child.text.strip())):
                    pack.files.append(PackFile(
                        child.tag, child.text.strip(), child.get('to'),
                        child.get('visible'), len(pack.files) + 1))
            elif child.tag == 'var' and child.get('for') in processing_dict:
                pack.variables.append(PackVariable(
                    processing_dict[child.get('for')], child.get('name'),
                    child.text and child.text.strip() or ''))
            elif child.tag == 'output':
                pack.outputs.append(PackOutput(
                    processing_dict[child.get('for')], child.text.strip()))
            elif child.tag == 'event':
                ref = child.get('ref') is not None \
                    and child.get('ref').split() or (None, None, None)
                operator[0] = ref[1]
                operator[1] = _operator_id(ref[1], len(ref) == 3 and ref[2])
                pack.events.append(PackEvent(
                    project_id, None, task_dict.get(ref[0]), child.get('task'),
                    operator[0], operator[1], child.get('operator'),
                    child.get('begin')))

        # Update current task
        if len(pack.events) and \
           pack_elt.find('events').get('inactive') != 'true':
            cls._set_current_task(pack)

        DBSession.add(pack)
        try:
            DBSession.commit()
        except IntegrityError as ref:
            DBSession.rollback()
            LOG.error(ref)
            return ref

        return pack.pack_id

    # -------------------------------------------------------------------------
    def xml(self):
        """Serialize a pack to a XML representation.

        :return: (:class:`lxml.etree.Element`)
        """
        # Create pack
        pack_elt = etree.Element('pack')
        pack_elt.set(
            '%sid' % XML_NS, 'pck%d.%d' % (self.project_id, self.pack_id))
        if self.recursive:
            pack_elt.set('recursive', 'true')
        pack_elt.set('created', self.created.isoformat().partition('.')[0])
        if self.created != self.updated:
            pack_elt.set('updated', self.updated.isoformat().partition('.')[0])
        etree.SubElement(pack_elt, 'label').text = self.label
        if self.description:
            etree.SubElement(pack_elt, 'description').text = \
                wrap(self.description, width=66, indent=12)
        export_file_set(pack_elt, self, 'file')
        export_file_set(pack_elt, self, 'resource')
        export_file_set(pack_elt, self, 'template')
        if self.note:
            etree.SubElement(pack_elt, 'note').text = self.note

        # Variables
        if self.variables:
            elt = etree.SubElement(pack_elt, 'variables')
            for var in self.variables:
                elt.append(var.xml())

        # Outputs
        if self.outputs:
            elt = etree.SubElement(pack_elt, 'outputs')
            for output in self.outputs:
                elt.append(output.xml())

        # Events
        if self.events:
            elt = etree.SubElement(pack_elt, 'events')
            for event in sorted(self.events, key=lambda k: k.begin):
                elt.append(event.xml())
            if self.task_id is None:
                elt.set('inactive', 'true')

        return pack_elt

    # -------------------------------------------------------------------------
    def update_sort(self):
        """Update ``sort`` field of PackFile table."""
        sorts = {'file': 1, 'resource': 1001, 'template': 2001}
        for item in sorted(self.files, key=lambda k: k.sort):
            item.sort = sorts[item.file_type]
            sorts[item.file_type] += 1

    # -------------------------------------------------------------------------
    @classmethod
    def _set_current_task(cls, pack):
        """Set the current task for the pack ``pack``.

        :param pack: (class:`Pack` instance)
        """
        last = None
        for event in pack.events:
            if last is None or event.begin is None or \
               (last.begin is not None and last.begin < event.begin):
                last = event
        if last is None:
            return

        if last.task_id and last.operator_type and \
           (last.operator_type == 'auto' or last.operator_id is not None):
            pack.task_id = last.task_id
            pack.operator_type = last.operator_type
            pack.operator_id = \
                last.operator_type != 'auto' and last.operator_id or None


# =============================================================================
class PackFile(Base):
    """SQLAlchemy-powered project pack file model."""
    # pylint: disable = locally-disabled, R0903

    __tablename__ = 'pack_file'
    __table_args__ = (
        ForeignKeyConstraint(
            ['project_id', 'pack_id'],
            ['pack.project_id', 'pack.pack_id'], ondelete='CASCADE'),
        {'mysql_engine': 'InnoDB'})
    project_id = Column(types.Integer, primary_key=True)
    pack_id = Column(types.Integer, primary_key=True)
    file_type = Column(
        types.Enum(*PCK_FILE_TYPES, name='pckfil_type_enum'), primary_key=True)
    path = Column(types.String(PATH_LEN), primary_key=True)
    target = Column(types.String(PATH_LEN))
    visible = Column(types.Boolean)
    sort = Column(types.Integer, default=0)

    # -------------------------------------------------------------------------
    def __init__(self, file_type, path, target=None, visible=None, sort=None):
        """Constructor method."""
        super(PackFile, self).__init__()
        self.file_type = file_type
        self.path = path.strip()[0:PATH_LEN]
        self.target = (target and target.strip()[0:PATH_LEN]) \
            or (file_type == 'template' and
                self.path.partition('/')[2][0:PATH_LEN]) or None
        self.visible = (visible is None and file_type == 'file' and True) \
            or (visible if isinstance(visible, bool) else (visible == 'true'))
        self.sort = sort


# =============================================================================
class PackVariable(Base):
    """SQLAlchemy-powered project pack variable model."""
    # pylint: disable = locally-disabled, R0903

    __tablename__ = 'pack_variable'
    __table_args__ = (
        ForeignKeyConstraint(
            ['project_id', 'pack_id'],
            ['pack.project_id', 'pack.pack_id'], ondelete='CASCADE'),
        {'mysql_engine': 'InnoDB'})
    project_id = Column(types.Integer, primary_key=True)
    pack_id = Column(types.Integer, primary_key=True)
    processing_id = Column(types.Integer, primary_key=True)
    name = Column(types.String(ID_LEN), primary_key=True)
    value = Column(types.String(VALUE_LEN))

    # -------------------------------------------------------------------------
    def __init__(self, processing_id, name, value):
        """Constructor method."""
        super(PackVariable, self).__init__()
        self.processing_id = processing_id
        self.name = name.strip()[0:ID_LEN]
        self.value = \
            isinstance(value, basestring) and value[0:VALUE_LEN] or value

    # -------------------------------------------------------------------------
    def xml(self):
        """Serialize a variable to a XML representation.

        :return: (:class:`lxml.etree.Element`)
        """
        var_elt = etree.Element('var')
        var_elt.set('for', 'prc%d.%d' % (self.project_id, self.processing_id))
        var_elt.set('name', self.name)
        var_elt.text = self.value
        return var_elt


# =============================================================================
class PackOutput(Base):
    """SQLAlchemy-powered project pack output model."""
    # pylint: disable = locally-disabled, R0903

    __tablename__ = 'pack_output'
    __table_args__ = (
        ForeignKeyConstraint(
            ['project_id', 'pack_id'],
            ['pack.project_id', 'pack.pack_id'], ondelete='CASCADE'),
        {'mysql_engine': 'InnoDB'})
    project_id = Column(types.Integer, primary_key=True)
    pack_id = Column(types.Integer, primary_key=True)
    processing_id = Column(types.Integer, primary_key=True)
    path = Column(types.String(PATH_LEN))

    # -------------------------------------------------------------------------
    def __init__(self, processing_id, path):
        """Constructor method."""
        super(PackOutput, self).__init__()
        self.processing_id = processing_id
        self.path = path.strip()[0:PATH_LEN]

    # -------------------------------------------------------------------------
    def xml(self):
        """Serialize an output to a XML representation.

        :return: (:class:`lxml.etree.Element`)
        """
        output_elt = etree.Element('output')
        output_elt.set(
            'for', 'prc%d.%d' % (self.project_id, self.processing_id))
        output_elt.text = self.path
        return output_elt


# =============================================================================
class PackEvent(Base):
    """SQLAlchemy-powered project pack task event model."""
    # pylint: disable = locally-disabled, R0902

    __tablename__ = 'pack_event'
    __table_args__ = (
        ForeignKeyConstraint(
            ['project_id', 'pack_id'],
            ['pack.project_id', 'pack.pack_id'], ondelete='CASCADE'),
        {'mysql_engine': 'InnoDB'})
    project_id = Column(types.Integer, primary_key=True)
    pack_id = Column(types.Integer, primary_key=True)
    begin = Column(types.DateTime, primary_key=True, default=datetime.now)
    task_id = Column(types.Integer)
    task_label = Column(types.String(LABEL_LEN), nullable=False)
    operator_type = Column(
        types.Enum(*OPERATOR_TYPES, name='operatortype_enum'))
    operator_id = Column(types.Integer)
    operator_label = Column(types.String(LABEL_LEN + 15), nullable=False)

    # -------------------------------------------------------------------------
    def __init__(self, project_id, pack_id, task_id, task_label,
                 operator_type, operator_id, operator_label, begin=None):
        """Constructor method."""
        # pylint: disable = locally-disabled, R0913
        super(PackEvent, self).__init__()
        self.project_id = project_id
        self.pack_id = pack_id
        if isinstance(begin, basestring):
            if '.' not in begin:
                begin = '%s.000000' % begin
            self.begin = datetime.strptime(begin, '%Y-%m-%dT%H:%M:%S.%f')
        else:
            self.begin = begin
        self.task_id = task_id
        self.task_label = normalize_spaces(task_label, LABEL_LEN)
        self.operator_type = operator_type
        self.operator_id = operator_id
        self.operator_label = normalize_spaces(operator_label, LABEL_LEN + 15)

    # -------------------------------------------------------------------------
    def xml(self):
        """Serialize an event to a XML representation.

        :return: (:class:`lxml.etree.Element`)
        """
        event_elt = etree.Element('event')
        event_elt.set('task', self.task_label)
        event_elt.set('operator', self.operator_label)

        if self.operator_type == 'user':
            user = DBSession.query(User.login).filter_by(
                user_id=self.operator_id).first()
            if user is not None:
                event_elt.set(
                    'ref', 'tsk%d.%d user %s' % (
                        self.project_id, self.task_id or 0, user[0]))
        elif self.operator_type == 'role':
            event_elt.set(
                'ref', 'tsk%d.%d role rol%d.%d' % (
                    self.project_id, self.task_id or 0, self.project_id,
                    self.operator_id or 0))
        else:
            event_elt.set(
                'ref', 'tsk%d.%d auto' % (self.project_id, self.task_id or 0))

        event_elt.set('begin', self.begin.isoformat())

        return event_elt
