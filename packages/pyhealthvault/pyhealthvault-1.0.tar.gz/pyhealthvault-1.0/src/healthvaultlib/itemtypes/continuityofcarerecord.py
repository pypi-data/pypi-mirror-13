from lxml import etree

from healthvaultlib.utils.xmlutils import XmlUtils
from healthvaultlib.itemtypes.healthrecorditem import HealthRecordItem


class ContinuityOfCareRecord(HealthRecordItem):

    def __init__(self, thing_xml=None):
        super(ContinuityOfCareRecord, self).__init__()
        self.type_id = '1e1ccbfc-a55d-4d91-8940-fa2fbf73c195'
        if thing_xml is not None:
            self.thing_xml = thing_xml
            self.parse_thing()

    def __str__(self):
        return 'ContinuityOfCareRecord'

    def parse_thing(self):
        super(ContinuityOfCareRecord, self).parse_thing()
        xmlutils = XmlUtils(self.thing_xml)

    def write_xml(self):
        thing = super(ContinuityOfCareRecord, self).write_xml()
        data_xml = etree.Element('data-xml')
        continuityofcarerecord = etree.Element('continuityofcarerecord')

        data_xml.append(continuityofcarerecord)
        thing.append(data_xml)
        return thing
