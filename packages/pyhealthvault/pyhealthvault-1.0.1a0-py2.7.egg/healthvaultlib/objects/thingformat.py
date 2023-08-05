from lxml import etree


class ThingFormat():

    def __init__(self):
        self.sections = []
        self.xml = None

    def write_xml(self):
        _format = etree.Element('format')
        if self.sections:
            self.add_sections(_format)
        if 'xml' in self.sections:
            xml = etree.Element('xml')
            if self.xml is not None:
                xml.append(etree.fromstring(self.xml))
            _format.append(xml)
        return _format

    def add_sections(self, _filter):
        for i in self.sections:
            if i in ['core', 'audits', 'effectivepermissions', 'digitalsignatures', 'tags', 'blobpayload']:
                section = etree.Element('section')
                section.text = i
                _filter.append(section)
