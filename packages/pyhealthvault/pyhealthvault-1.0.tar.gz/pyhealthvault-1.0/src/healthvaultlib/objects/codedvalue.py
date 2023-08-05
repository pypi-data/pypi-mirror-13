from lxml import etree
from healthvaultlib.utils.xmlutils import XmlUtils


class CodedValue():

    def __init__(self, coded_value_xml=None):
        self.text = None
        self.value = None
        self.family = None
        self._type = None
        self.version = None

        if coded_value_xml is not None:
            xmlutils = XmlUtils(coded_value_xml)
            self.text = xmlutils.get_string_by_xpath('text/text()')
            self.value = xmlutils.get_string_by_xpath('code/value/text()')
            self.family = xmlutils.get_string_by_xpath('code/family/text()')
            self._type = xmlutils.get_string_by_xpath('code/type/text()')
            self.version = xmlutils.get_string_by_xpath('code/version/text()')

    def write_xml(self, node_name):
        codable_value = etree.element(node_name)
        codable_value.text = self.text

        code = etree.Element('code')

        value = etree.Element('value')
        value.text = self.value
        code.append(value)

        family = etree.Element('family')
        family.text = self.family
        code.append(family)

        _type = etree.Element('type')
        _type.text = self._type
        code.append(_type)

        version = etree.Element('version')
        version.text = self.version
        code.append(version)

        codable_value.append(code)

        return codable_value
