from healthvaultlib.utils.xmlutils import XmlUtils
from healthvaultlib.objects.permission import Permission


class AuthRule:
    
    def __init__(self, rule_xml=None):
        self.name = ''
        self.reason = {}
        self.display_flags = 0
        self.permissions = 0
        self.typeids = []

        if rule_xml is not None:
            self.parse_xml(rule_xml)

    def parse_xml(self, rule_xml):
        xmlutils = XmlUtils(rule_xml)
        self.name = xmlutils.get_string('name')
        self.reason = self.get_culture_specific_dictionary(rule_xml, 'reason')
        self.display_flags = xmlutils.get_int('display-flags/text()')
        self.permissions = Permission(rule_xml)

        for typeid in rule_xml.xpath('target-set/type-id'):
            self.typeids.append(typeid.xpath('text()')[0])

    def get_culture_specific_dictionary(self, info_element, key):
        XMLNS = '{http://www.w3.org/XML/1998/namespace}'
        result = {}
        for entry in info_element.xpath('application/' + key):
            lang = entry.get(XMLNS + 'lang', default='')
            result[lang] = entry.xpath('text()')[0]
        return result
