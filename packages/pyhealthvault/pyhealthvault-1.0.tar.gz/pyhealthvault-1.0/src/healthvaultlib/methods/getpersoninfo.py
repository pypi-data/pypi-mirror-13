from lxml import etree
from healthvaultlib.methods.method import Method
from healthvaultlib.objects.personinfo import PersonInfo
from healthvaultlib.methods.methodbase import RequestBase, ResponseBase

class GetPersonInfoRequest(RequestBase):
    
    def __init__(self):
        super(GetPersonInfoRequest, self).__init__()
        self.name = 'GetPersonInfo'
        self.version = 1

    def get_info(self):
        info = etree.Element('info')
        return info

class GetPersonInfoResponse(ResponseBase):

    def __init__(self):
        super(GetPersonInfoResponse, self).__init__()
        self.personinfo = None
        self.name = 'GetPersonInfo'
        self.version = 1

    def parse_response(self, response):
        self.parse_info(response)
        self.personinfo = PersonInfo(self.info.xpath('person-info')[0])

class GetPersonInfo(Method):
    
    def __init__(self):
        self.request = GetPersonInfoRequest()
        self.response = GetPersonInfoResponse()
