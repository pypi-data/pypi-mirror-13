from lxml import etree

from healthvaultlib.methods.method import Method
from healthvaultlib.objects.updatedrecord import UpdatedRecord
from healthvaultlib.methods.methodbase import RequestBase, ResponseBase


class GetUpdatedRecordsForApplicationRequest(RequestBase):
    '''
        Gets a list of records for an application with things that have
        been updated since a specified date.

        Attributes:
            updated_date    Optionally provide an updated since date,
                            of type datetime.datetime
    '''

    def __init__(self):
        super(GetUpdatedRecordsForApplicationRequest, self).__init__()
        self.name = 'GetUpdatedRecordsForApplication'
        self.version = 1
        self.update_date = None

    def get_info(self):
        info = etree.Element('info')
        if self.update_date is not None:
            update_date = etree.Element('update-date')
            update_date.text = self.update_date.isoformat()
            info.append(update_date)
        return info


class GetUpdatedRecordsForApplicationResponse(ResponseBase):

    def __init__(self):
        super(GetUpdatedRecordsForApplicationResponse, self).__init__()
        self.name = 'GetUpdatedRecordsForApplication'
        self.version = 1
        self.updated_records = []

    def parse_response(self, response):
        self.parse_info(response)
        for i in self.info.xpath('record-id'):
            self.updated_records.append(UpdatedRecord(i))


class GetUpdatedRecordsForApplication(Method):

    def __init__(self):
        self.request = GetUpdatedRecordsForApplicationRequest()
        self.response = GetUpdatedRecordsForApplicationResponse()
