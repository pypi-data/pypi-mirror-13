from healthvaultlib.utils.xmlutils import XmlUtils
from healthvaultlib.objects.record import Record


class PersonInfo():

    def __init__(self, info_element=None):
        self.personid = None
        self.name = None
        self.selected_record_id = None
        self.records = []
        if info_element is not None:
            self.parse_xml(info_element)

    def parse_xml(self, info_element):
        xmlutils = XmlUtils(info_element)
        self.personid = xmlutils.get_string_by_xpath('person-id/text()')
        self.name = xmlutils.get_string_by_xpath('name/text()')
        self.selected_record_id = xmlutils.get_string_by_xpath('selected-record-id/text()')
        records = info_element.xpath('record')
        for i in records:
            self.records.append(Record(i))
