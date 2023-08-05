from lxml import etree
from healthvaultlib.methods.method import Method
from healthvaultlib.objects.servicedefinition import ServiceDefinition
from healthvaultlib.methods.methodbase import RequestBase, ResponseBase

class GetServiceDefinitionRequest(RequestBase):
    
    def __init__(self, response_sections, updated_date):
        super(GetServiceDefinitionRequest, self).__init__()
        self.name = 'GetServiceDefinition'
        self.version = 2
        self.updated_date = updated_date
        self.response_sections = response_sections

    def get_info(self):
        info = etree.Element('info')
        if self.updated_date is not None:
            updated_date = etree.Element('updated-date')
            updated_date.text = self.updated_date.isoformat()
            info.append(updated_date)
        if self.response_sections != []:
            response_sections = etree.Element('response-sections')
            for i in self.response_sections:
                section = etree.Element('section')
                section.text = i
                response_sections.append(section)
            info.append(response_sections)
        return info

class GetServiceDefinitionResponse(ResponseBase):

    def __init__(self):
        super(GetServiceDefinitionResponse, self).__init__()
        self.name = 'GetServiceDefinition'
        self.version = 2
        self.service_definition = None

    def parse_response(self, response):
        self.parse_info(response)
        self.service_definition = ServiceDefinition(self.info)

class GetServiceDefinition(Method):
    
    def __init__(self, response_sections, updated_date=None):
        self.request = GetServiceDefinitionRequest(response_sections, updated_date)
        self.response = GetServiceDefinitionResponse()
