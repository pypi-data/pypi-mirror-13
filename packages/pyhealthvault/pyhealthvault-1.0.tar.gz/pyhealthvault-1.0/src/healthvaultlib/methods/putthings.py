from lxml import etree

from healthvaultlib.methods.method import Method
from healthvaultlib.methods.methodbase import RequestBase, ResponseBase
from healthvaultlib.objects.thingkey import ThingKey

class PutThingsRequest(RequestBase):
    
    def __init__(self, items):
        super(PutThingsRequest, self).__init__()
        self.name = 'PutThings'
        self.version = 2
        self.healthrecorditems = items

    def get_info(self):
        info = etree.Element('info')
        for item in self.healthrecorditems:
            info.append(item.write_xml())
        return info
        
class PutThingsResponse(ResponseBase):

    def __init__(self, items):
        super(PutThingsResponse, self).__init__()
        self.name = 'PutThings'
        self.version = 1
        self.healthrecorditems = items

    def parse_response(self, response):
        self.parse_info(response)
        i = 0
        for key in self.info.xpath('thing-id'):
            thing_key = ThingKey(key)
            self.healthrecorditems[i].key = thing_key
            i += 1


class PutThings(Method):

    def __init__(self, items):
        self.request = PutThingsRequest(items)
        self.response = PutThingsResponse(items)
