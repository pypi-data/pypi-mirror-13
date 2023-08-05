from healthvaultlib.utils.xmlutils import XmlUtils


class XmlMethodVersion:

    def __init__(self, version_xml=None):
        self.number = None
        self.request_schema_url = None
        self.response_schema_url = None

        if version_xml is not None:
            self.parse_xml(version_xml)

    def parse_xml(self, version_xml):
        xmlutils = XmlUtils(version_xml)
        self.number = version_xml.get('number')
        self.request_schema_url = xmlutils.get_string_by_xpath('request-schema-url/text()')
        self.response_schema_url = xmlutils.get_string_by_xpath('response-schema-url/text()')
