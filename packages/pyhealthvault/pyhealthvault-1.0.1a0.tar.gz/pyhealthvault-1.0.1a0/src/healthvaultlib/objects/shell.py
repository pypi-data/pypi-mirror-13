from healthvaultlib.utils.xmlutils import XmlUtils
from healthvaultlib.objects.shellredirecttoken import ShellRedirectToken


class Shell:
    def __init__(self, shell_xml=None):
        self.url = None
        self.redirect_url = None
        self.redirect_token = []

        if shell_xml is not None:
            self.parse_xml(shell_xml)

    def parse_xml(self, shell_xml):
        xmlutils = XmlUtils(shell_xml)
        self.url = xmlutils.get_string_by_xpath('url/text()')
        self.redirect_url = xmlutils.get_string_by_xpath('redirect-url/text()')

        for i in shell_xml.xpath('redirect-token'):
            self.redirect_token.append(ShellRedirectToken(i))
