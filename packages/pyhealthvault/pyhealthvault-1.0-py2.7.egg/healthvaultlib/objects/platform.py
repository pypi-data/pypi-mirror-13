from healthvaultlib.utils.xmlutils import XmlUtils


class Platform:

    def __init__(self, platform_xml=None):
        self.url = None
        self.version = None
        self.configuration = {}

        if platform_xml is not None:
            self.parse_xml(platform_xml)

    def parse_xml(self, platform_xml):
        xmlutils = XmlUtils(platform_xml)
        self.url = xmlutils.get_string_by_xpath('url/text()')
        self.version = xmlutils.get_string_by_xpath('version/text()')

        for i in platform_xml.xpath('configuration'):
            self.configuration[i.get('key')] = i.xpath('text()')[0]
