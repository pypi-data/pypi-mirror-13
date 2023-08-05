from lxml import etree

from healthvaultlib.utils.xmlutils import XmlUtils
from healthvaultlib.itemtypes.healthrecorditem import HealthRecordItem


class FamilyHistory(HealthRecordItem):

    def __init__(self, thing_xml=None):
        super(FamilyHistory, self).__init__()
        self.type_id = '4a04fcc8-19c1-4d59-a8c7-2031a03f21de'
        if thing_xml is not None:
            self.thing_xml = thing_xml
            self.parse_thing()

    def __str__(self):
        return 'FamilyHistory'

    def parse_thing(self):
        super(FamilyHistory, self).parse_thing()
        xmlutils = XmlUtils(self.thing_xml)

    def write_xml(self):
        thing = super(FamilyHistory, self).write_xml()
        data_xml = etree.Element('data-xml')
        familyhistory = etree.Element('familyhistory')

        data_xml.append(familyhistory)
        thing.append(data_xml)
        return thing
