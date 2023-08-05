from lxml import etree

from healthvaultlib.methods.method import Method
from healthvaultlib.utils.xmlutils import XmlUtils
from healthvaultlib.objects.personinfo import PersonInfo
from healthvaultlib.methods.methodbase import RequestBase, ResponseBase

class GetAuthorizedPeopleRequest(RequestBase):
    
    def __init__(self, parameters):
        super(GetAuthorizedPeopleRequest, self).__init__()
        self.name = 'GetAuthorizedPeople'
        self.version = 1
        self.parameters = parameters

    def get_info(self):
        info = etree.Element('info')
        info.append(self.parameters.get_info())
        return info
        
class GetAuthorizedPeopleResponse(ResponseBase):

    def __init__(self):
        super(GetAuthorizedPeopleResponse, self).__init__()
        self.name = 'GetAuthorizedPeople'
        self.version = 1
        self.authorized_people = []

    def parse_response(self, response):
        self.parse_info(response)
        for i in self.info.xpath('response-results/person-info'):
            self.authorized_people.append(PersonInfo(i))

        xmlutils = XmlUtils(self.info)
        self.more_results = xmlutils.get_bool_by_xpath('more-results')

class GetAuthorizedPeople(Method):

    def __init__(self, parameters):
        self.request = GetAuthorizedPeopleRequest(parameters)
        self.response = GetAuthorizedPeopleResponse()
