from lxml import etree

from healthvaultlib.utils.xmlutils import XmlUtils
from healthvaultlib.itemtypes.healthrecorditem import HealthRecordItem


class FamilyHistoryCondition(HealthRecordItem):

    def __init__(self, thing_xml=None):
        super(FamilyHistoryCondition, self).__init__()
        self.type_id = '6705549b-0e3d-474e-bfa7-8197ddd6786a'
        if thing_xml is not None:
            self.thing_xml = thing_xml
            self.parse_thing()

    def __str__(self):
        return 'FamilyHistoryCondition'

    def parse_thing(self):
        super(FamilyHistoryCondition, self).parse_thing()
        xmlutils = XmlUtils(self.thing_xml)

    def write_xml(self):
        thing = super(FamilyHistoryCondition, self).write_xml()
        data_xml = etree.Element('data-xml')
        familyhistorycondition = etree.Element('familyhistorycondition')

        data_xml.append(familyhistorycondition)
        thing.append(data_xml)
        return thing
