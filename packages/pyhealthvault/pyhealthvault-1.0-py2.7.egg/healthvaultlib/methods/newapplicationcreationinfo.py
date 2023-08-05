from lxml import etree
from healthvaultlib.methods.method import Method
from healthvaultlib.utils.xmlutils import XmlUtils
from healthvaultlib.methods.methodbase import RequestBase, ResponseBase


class NewApplicationCreationInfoRequest(RequestBase):
    
    def __init__(self):
        super(NewApplicationCreationInfoRequest, self).__init__()
        self.name = 'NewApplicationCreationInfo'
        self.version = 1

    def get_info(self):
        info = etree.Element('info')
        return info

class NewApplicationCreationInfoResponse(ResponseBase):

    def __init__(self):
        super(NewApplicationCreationInfoResponse, self).__init__()
        self.name = 'NewApplicationCreationInfo'
        self.version = 1

        self.app_id = None
        self.shared_secret = None
        self.app_token = None

    def parse_response(self, response):
        self.parse_info(response)
        xmlutils = XmlUtils(self.info)
        self.app_id = xmlutils.get_string_by_xpath('app-id/text()')
        self.shared_secret = xmlutils.get_string_by_xpath('shared-secret/text()')
        self.app_token = xmlutils.get_string_by_xpath('app-token/text()')

class NewApplicationCreationInfo(Method):

    def __init__(self):
        self.request = NewApplicationCreationInfoRequest()
        self.response = NewApplicationCreationInfoResponse()
