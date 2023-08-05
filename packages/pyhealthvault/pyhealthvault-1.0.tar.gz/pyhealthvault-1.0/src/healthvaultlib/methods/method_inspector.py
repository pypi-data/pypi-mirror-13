from lxml import etree

from healthvaultlib.methods.method import Method
from healthvaultlib.methods.methodbase import RequestBase, ResponseBase

class InspectorRequest(RequestBase):
    
    def __init__(self, parameters):
        super(InspectorRequest, self).__init__()
        self.name = 'GetAuthorizedPeople'
        self.version = 1
        self.parameters = parameters

    def get_info(self):
        info = etree.Element('info')
        info.append(self.parameters.get_info())
        return info
        
class InspectorResponse(ResponseBase):

    def __init__(self):
        super(InspectorResponse, self).__init__()
        self.name = 'GetAuthorizedPeople'
        self.version = 1

    def parse_response(self, response):
        self.parse_info(response)

class Inspector(Method):

    def __init__(self, parameters):
        self.request = InspectorRequest(parameters)
        self.response = InspectorResponse()
