from healthvaultlib.utils.xmlutils import XmlUtils


class MeaningfulUse:

    def __init__(self, meaningful_use_xml=None):
        self.enabled = None
        self.configuration = {}

        if meaningful_use_xml is not None:
            self.parse_xml(meaningful_use_xml)

    def parse_xml(self, meaningful_use_xml):
        xmlutils = XmlUtils(meaningful_use_xml)
        self.enabled = xmlutils.get_bool_by_xpath('enabled/text()')

        for i in meaningful_use_xml.xpath('configuration'):
            self.configuration[i.get('key')] = i.xpath('text()')[0]
