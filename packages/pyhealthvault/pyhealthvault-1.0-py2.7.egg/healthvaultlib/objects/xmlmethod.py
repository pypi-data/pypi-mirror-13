from healthvaultlib.utils.xmlutils import XmlUtils
from healthvaultlib.objects.xmlmethodversion import XmlMethodVersion


class XmlMethod:
    def __init__(self, method_xml=None):
        self.name = None
        self.version = []

        if method_xml is not None:
            self.parse_xml(method_xml)

    def parse_xml(self, method_xml):
        xmlutils = XmlUtils(method_xml)
        self.name = xmlutils.get_string_by_xpath('name/text()')

        for i in method_xml.xpath('version'):
            self.version.append(XmlMethodVersion(i))
