from lxml import etree

from healthvaultlib.methods.method import Method
from healthvaultlib.objects.thingkey import ThingKey
from healthvaultlib.methods.methodbase import RequestBase, ResponseBase

class RemoveThingsRequest(RequestBase):
    
    def __init__(self, keys):
        super(RemoveThingsRequest, self).__init__()
        self.name = 'RemoveThings'
        self.version = 1
        self.keys = keys

    def get_info(self):
        info = etree.Element('info')
        for key in self.keys:
            info.append(key.write_xml())
        return info
        
class RemoveThingsResponse(ResponseBase):

    def __init__(self):
        super(RemoveThingsResponse, self).__init__()
        self.thing_keys = []
        self.name = 'RemoveThings'
        self.version = 1
        self.NSMAP = {'wc' : 'urn:com.microsoft.wc.methods.response.any'}

    def parse_response(self, response):
        return None

class RemoveThings(Method):

    def __init__(self, items):
        self.request = RemoveThingsRequest(items)
        self.response = RemoveThingsResponse()