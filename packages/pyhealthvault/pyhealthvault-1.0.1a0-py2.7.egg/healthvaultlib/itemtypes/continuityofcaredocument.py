from lxml import etree

from healthvaultlib.utils.xmlutils import XmlUtils
from healthvaultlib.itemtypes.healthrecorditem import HealthRecordItem


class ContinuityOfCareDocument(HealthRecordItem):

    def __init__(self, thing_xml=None):
        super(ContinuityOfCareDocument, self).__init__()
        self.type_id = '9c48a2b8-952c-4f5a-935d-f3292326bf54'
        if thing_xml is not None:
            self.thing_xml = thing_xml
            self.parse_thing()

    def __str__(self):
        return 'ContinuityOfCareDocument'

    def parse_thing(self):
        super(ContinuityOfCareDocument, self).parse_thing()
        xmlutils = XmlUtils(self.thing_xml)

    def write_xml(self):
        thing = super(ContinuityOfCareDocument, self).write_xml()
        data_xml = etree.Element('data-xml')
        continuityofcaredocument = etree.Element('continuityofcaredocument')

        data_xml.append(continuityofcaredocument)
        thing.append(data_xml)
        return thing
