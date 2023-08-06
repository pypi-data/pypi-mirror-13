# $Id: processings.py 95fb4057a3cf 2015/09/27 09:04:08 Patrick $
"""SQLAlchemy-powered model definition for project processings."""
# pylint: disable = locally-disabled, super-on-old-class

from logging import getLogger
from lxml import etree
from sqlalchemy import Column, ForeignKey, types
from sqlalchemy.schema import ForeignKeyConstraint, UniqueConstraint
from sqlalchemy.orm import relationship
from sqlalchemy.exc import IntegrityError

from ..lib.utils import _, normalize_spaces, export_file_set, wrap
from . import ID_LEN, LABEL_LEN, DESCRIPTION_LEN, PATH_LEN, VALUE_LEN
from . import Base, DBSession


LOG = getLogger(__name__)
PRC_FILE_TYPES = ('resource', 'template')
ADD2PACK_TARGETS = {
    'result2files': _('result in files'),
    'result2resources': _('result in resources'),
    'result2templates': _('result in templates'),
    'output2files': _('full output in files'),
    'output2resources': _('full output in resources'),
    'output2templates': _('full output in templates'),
    'smart': _('smart packing')}
XML_NS = '{http://www.w3.org/XML/1998/namespace}'


# =============================================================================
class Processing(Base):
    """SQLAlchemy-powered project processing model."""

    __tablename__ = 'processing'
    __table_args__ = (
        UniqueConstraint('project_id', 'label'), {'mysql_engine': 'InnoDB'})

    project_id = Column(
        types.Integer,
        ForeignKey('project.project_id', ondelete='CASCADE'),
        primary_key=True)
    processing_id = Column(types.Integer, primary_key=True)
    label = Column(types.String(LABEL_LEN), nullable=False)
    description = Column(types.String(DESCRIPTION_LEN))
    processor = Column(types.String(ID_LEN), nullable=False)
    output = Column(types.String(PATH_LEN))
    add2pack = Column(
        types.Enum(*ADD2PACK_TARGETS.keys(), name='add2pack_type_enum'))
    indirect = Column(types.Boolean, default=False)
    variables = relationship('ProcessingVariable')
    files = relationship('ProcessingFile')

    # -------------------------------------------------------------------------
    def __init__(self, project_id, label, description, processor, output=None,
                 add2pack=None, indirect=False):
        """Constructor method."""
        # pylint: disable = locally-disabled, R0913
        super(Processing, self).__init__()
        self.project_id = project_id
        self.label = normalize_spaces(label, LABEL_LEN)
        self.description = normalize_spaces(description, DESCRIPTION_LEN)
        self.processor = processor.strip()[0:ID_LEN]
        self.output = output and output.strip()[0:PATH_LEN]
        self.add2pack = add2pack
        self.indirect = indirect

    # -------------------------------------------------------------------------
    @classmethod
    def load(cls, project_id, processing_elt, check_if_exists=True):
        """Load a processing from a XML element.

        :param processing_elt: (:class:`lxml.etree.Element` instance)
            Processing XML element.
        :param check_if_exists: (boolean, default=True)
            Check if processing already exists before inserting.
        :return: (:class:`pyramid.i18n.TranslationString` or integer)
            Error message or integer.
        """
        if processing_elt is None:
            return _('nothing to do!')

        label = normalize_spaces(processing_elt.findtext('label'), LABEL_LEN)
        if check_if_exists:
            processing = DBSession.query(cls).filter_by(
                project_id=project_id, label=label).first()
            if processing is not None:
                return _('Processing "${l}" already exists.', {'l': label})

        output = processing_elt.find('output')
        processing = cls(
            project_id, label,
            processing_elt.findtext('description'),
            processing_elt.findtext('processor').strip(),
            output is not None and output.text or None,
            output is not None and output.get('add2pack') or None,
            processing_elt.get('indirect', False) == 'true')

        # Load variables, resources and templates
        for child in processing_elt.iterdescendants(tag=etree.Element):
            if child.tag == 'var':
                if child.get('visible') is not None or child.text is not None:
                    processing.variables.append(ProcessingVariable(
                        child.get('name'),
                        '' if child.text is not None and not child.text.strip()
                        else child.text, child.get('visible')))
            if child.tag in PRC_FILE_TYPES:
                processing.files.append(ProcessingFile(
                    child.tag, child.text.strip(), child.get('to'),
                    len(processing.files) + 1))

        DBSession.add(processing)
        try:
            DBSession.commit()
        except IntegrityError as error:
            DBSession.rollback()
            LOG.error(error)
            return error
        return processing.processing_id

    # -------------------------------------------------------------------------
    def xml(self, processor):
        """Serialize a processing to a XML representation.

        :param processor: (:class:`lxml.etree.ElementTree` instance)
            Processor of current processing.
        :return: (:class:`lxml.etree.Element`)
        """
        proc_elt = etree.Element('processing')
        proc_elt.set('%sid' % XML_NS,
                     'prc%d.%d' % (self.project_id, self.processing_id))
        etree.SubElement(proc_elt, 'label').text = self.label
        if self.indirect:
            proc_elt.set('indirect', 'true')
        if self.description:
            etree.SubElement(proc_elt, 'description').text = \
                wrap(self.description, width=66, indent=12)
        etree.SubElement(proc_elt, 'processor').text = self.processor

        # Variables
        if processor is not None:
            self._export_variables(proc_elt, processor)

        # Files
        export_file_set(proc_elt, self, 'resource')
        export_file_set(proc_elt, self, 'template')
        if self.output or self.add2pack:
            elt = etree.SubElement(proc_elt, 'output')
            elt.text = self.output
            if self.add2pack:
                elt.set('add2pack', self.add2pack)

        return proc_elt

    # -------------------------------------------------------------------------
    def export_build_variables(self, proc_elt, processor, pack, values):
        """Read variable definitions in processor tree and fill ``variables``
        XML structure for a build.

        :param proc_elt: (:class:`lxml.etree.Element` instance)
            Processing element that binds the result.
        :param processor: (:class:`lxml.etree.ElementTree` instance)
            Processor of current processing.
        :param pack: (:class:`~.models.packs.Pack` instance)
            Current pack.
        :param values: (dictionary)
            Variables values.
        """
        # Read values
        processing_vars = dict([(k.name, k.default) for k in self.variables])
        pack_vars = dict([(k.name, k.value) for k in pack.variables
                          if k.processing_id == self.processing_id])

        vars_elt = etree.Element('variables')
        for var in processor.findall('processor/variables/group/var'):
            name = var.get('name')
            value = None
            if name in values:
                value = values[name]
            elif name in pack_vars:
                value = pack_vars[name]
            elif name in processing_vars:
                value = processing_vars[name]
            if value is not None and var.get('type') == 'boolean':
                value = 'true' if value and value != 'false' else 'false'
            if value is not None and value != var.findtext('default'):
                etree.SubElement(vars_elt, 'var', name=name).text = \
                    unicode(value)

        if len(vars_elt):
            proc_elt.append(vars_elt)

    # -------------------------------------------------------------------------
    def update_sort(self):
        """Update ``sort`` field of ProcessingFile table."""
        sorts = {'resource': 1001, 'template': 2001}
        for item in sorted(self.files, key=lambda k: k.sort):
            item.sort = sorts[item.file_type]
            sorts[item.file_type] += 1

    # -------------------------------------------------------------------------
    def _export_variables(self, proc_elt, processor):
        """Read variable definitions in processor tree and fill ``variables``
        XML structure.

        :param proc_elt: (:class:`lxml.etree.Element` instance)
            Processing element that binds the result.
        :param processor: (:class:`lxml.etree.ElementTree` instance)
            Processor of current processing.
        """
        defaults = dict([
            (k.name, (k.default, k.visible)) for k in self.variables])
        if len(defaults) == 0:
            return

        # Browse processor variables
        vars_elt = etree.Element('variables')
        for var in processor.findall('processor/variables/group/var'):
            name = var.get('name')
            if name in defaults:
                elt = etree.Element('var', name=name)
                if defaults[name][0] is not None \
                   and defaults[name][0] != var.findtext('default'):
                    elt.text = defaults[name][0] or ' '
                if defaults[name][1] is not None and \
                        bool(defaults[name][1]) != bool(var.get('visible')):
                    elt.set('visible', str(defaults[name][1]).lower())
                if elt.text is not None or elt.get('visible') is not None:
                    vars_elt.append(elt)

        if len(vars_elt):
            proc_elt.append(vars_elt)


# =============================================================================
class ProcessingVariable(Base):
    """SQLAlchemy-powered project processing variable model."""
    # pylint: disable = locally-disabled, R0903

    __tablename__ = 'processing_variable'
    __table_args__ = (
        ForeignKeyConstraint(
            ['project_id', 'processing_id'],
            ['processing.project_id', 'processing.processing_id'],
            ondelete='CASCADE'),
        {'mysql_engine': 'InnoDB'})
    project_id = Column(types.Integer, primary_key=True)
    processing_id = Column(types.Integer, primary_key=True)
    name = Column(types.String(ID_LEN), primary_key=True)
    default = Column(types.String(VALUE_LEN))
    visible = Column(types.Boolean)

    # -------------------------------------------------------------------------
    def __init__(self, name, default, visible=None):
        """Constructor method."""
        super(ProcessingVariable, self).__init__()
        self.name = name.strip()[0:ID_LEN]
        self.default = \
            isinstance(default, basestring) and default[0:VALUE_LEN] or default
        if visible is not None:
            self.visible = \
                visible if isinstance(visible, bool) else (visible == 'true')


# =============================================================================
class ProcessingFile(Base):
    """SQLAlchemy-powered project processing file model."""
    # pylint: disable = locally-disabled, R0903

    __tablename__ = 'processing_file'
    __table_args__ = (
        ForeignKeyConstraint(
            ['project_id', 'processing_id'],
            ['processing.project_id', 'processing.processing_id'],
            ondelete='CASCADE'),
        {'mysql_engine': 'InnoDB'})
    project_id = Column(types.Integer, primary_key=True)
    processing_id = Column(types.Integer, primary_key=True)
    file_type = Column(
        types.Enum(*PRC_FILE_TYPES, name='prcfil_type_enum'), primary_key=True)
    path = Column(types.String(PATH_LEN), primary_key=True)
    target = Column(types.String(PATH_LEN))
    sort = Column(types.Integer, default=0)

    # -------------------------------------------------------------------------
    def __init__(self, file_type, path, target=None, sort=None):
        """Constructor method."""
        super(ProcessingFile, self).__init__()
        self.file_type = file_type
        self.path = path.strip()[0:PATH_LEN]
        self.target = (target and target.strip()[0:PATH_LEN]) \
            or (file_type == 'template' and
                self.path.partition('/')[2][0:PATH_LEN]) or None
        self.sort = sort
