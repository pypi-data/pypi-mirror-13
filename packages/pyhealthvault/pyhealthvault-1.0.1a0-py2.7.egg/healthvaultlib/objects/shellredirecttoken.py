from healthvaultlib.utils.xmlutils import XmlUtils


class ShellRedirectToken:

    def __init__(self, token_xml=None):
        self.token = None
        self.description = None
        self.querystring_parameters = []

        if token_xml is not None:
            self.parse_xml(token_xml)

    def parse_xml(self, token_xml):
        xmlutils = XmlUtils(token_xml)
        self.token = xmlutils.get_string_by_xpath('token/text()')
        self.description = xmlutils.get_string_by_xpath('description/text()')
        self.querystring_parameters = xmlutils.get_string_by_xpath('querystring-parameters/text()').split(',')
