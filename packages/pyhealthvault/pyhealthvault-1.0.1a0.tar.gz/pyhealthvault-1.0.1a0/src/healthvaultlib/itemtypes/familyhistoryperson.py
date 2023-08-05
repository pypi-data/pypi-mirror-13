from lxml import etree

from healthvaultlib.utils.xmlutils import XmlUtils
from healthvaultlib.itemtypes.healthrecorditem import HealthRecordItem


class FamilyHistoryPerson(HealthRecordItem):

    def __init__(self, thing_xml=None):
        super(FamilyHistoryPerson, self).__init__()
        self.type_id = 'cc23422c-4fba-4a23-b52a-c01d6cd53fdf'
        if thing_xml is not None:
            self.thing_xml = thing_xml
            self.parse_thing()

    def __str__(self):
        return 'FamilyHistoryPerson'

    def parse_thing(self):
        super(FamilyHistoryPerson, self).parse_thing()
        xmlutils = XmlUtils(self.thing_xml)

    def write_xml(self):
        thing = super(FamilyHistoryPerson, self).write_xml()
        data_xml = etree.Element('data-xml')
        familyhistoryperson = etree.Element('familyhistoryperson')

        data_xml.append(familyhistoryperson)
        thing.append(data_xml)
        return thing
