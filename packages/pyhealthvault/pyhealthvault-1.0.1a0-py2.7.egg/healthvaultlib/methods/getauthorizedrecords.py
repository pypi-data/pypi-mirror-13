from lxml import etree

from healthvaultlib.methods.method import Method
from healthvaultlib.objects.record import Record
from healthvaultlib.methods.methodbase import RequestBase, ResponseBase


class GetAuthorizedRecordsRequest(RequestBase):

    def __init__(self, recordids):
        '''
            :param recordids: List of record ids whose info is to be fetched
            :type recordids: Array of str
        '''
        super(GetAuthorizedRecordsRequest, self).__init__()
        self.name = 'GetAuthorizedRecords'
        self.version = 1
        self.ids = recordids

    def get_info(self):
        info = etree.Element('info')
        for i in self.ids:
            id_node = etree.Element('id')
            id_node.text = i
            info.append(id_node)
        return info


class GetAuthorizedRecordsResponse(ResponseBase):

    def __init__(self):
        super(GetAuthorizedRecordsResponse, self).__init__()
        self.name = 'GetAuthorizedRecords'
        self.version = 1
        self.records = []

    def parse_response(self, response):
        self.parse_info(response)
        for i in self.info.xpath('record'):
            self.records.append(Record(i))


class GetAuthorizedRecords(Method):

    def __init__(self, recordids):
        '''
            :param recordids: List of record ids whose info is to be fetched
            :type recordids: Array of str
        '''
        self.request = GetAuthorizedRecordsRequest(recordids)
        self.response = GetAuthorizedRecordsResponse()
