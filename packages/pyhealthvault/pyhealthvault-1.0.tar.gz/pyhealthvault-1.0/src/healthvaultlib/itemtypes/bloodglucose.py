from lxml import etree

from healthvaultlib.utils.xmlutils import XmlUtils
from healthvaultlib.itemtypes.healthrecorditem import HealthRecordItem


class BloodGlucose(HealthRecordItem):

    def __init__(self, thing_xml=None):
        super(BloodGlucose, self).__init__()
        self.type_id = '879e7c04-4e8a-4707-9ad3-b054df467ce4'
        if thing_xml is not None:
            self.thing_xml = thing_xml
            self.parse_thing()

    def __str__(self):
        return 'BloodGlucose'

    def parse_thing(self):
        super(BloodGlucose, self).parse_thing()
        xmlutils = XmlUtils(self.thing_xml)

    def write_xml(self):
        thing = super(BloodGlucose, self).write_xml()
        data_xml = etree.Element('data-xml')
        bloodglucose = etree.Element('bloodglucose')

        data_xml.append(bloodglucose)
        thing.append(data_xml)
        return thing
