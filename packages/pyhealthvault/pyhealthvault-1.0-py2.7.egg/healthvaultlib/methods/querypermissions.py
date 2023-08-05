from lxml import etree

from healthvaultlib.methods.method import Method
from healthvaultlib.objects.thingtypepermissions import ThingTypePermissions
from healthvaultlib.methods.methodbase import RequestBase, ResponseBase

class QueryPermissionsRequest(RequestBase):
    
    def __init__(self, typeids):
        super(QueryPermissionsRequest, self).__init__()
        self.name = 'QueryPermissions'
        self.version = 1
        self.typeids = typeids

    def get_info(self):
        info = etree.Element('info')
        for typeid in self.typeids:
            thing_type_id = etree.Element('thing-type-id')
            thing_type_id.text = typeid
            info.append(thing_type_id)
        return info
        
class QueryPermissionsResponse(ResponseBase):

    def __init__(self):
        super(QueryPermissionsResponse, self).__init__()
        self.permissions = []
        self.name = 'QueryPermissions'
        self.version = 1

    def parse_response(self, response):
        self.parse_info(response)
        for perm in self.info.xpath('thing-type-permission'):
            self.permissions.append(ThingTypePermissions(perm))
            

class QueryPermissions(Method):

    def __init__(self, typeids):
        self.request = QueryPermissionsRequest(typeids)
        self.response = QueryPermissionsResponse()
