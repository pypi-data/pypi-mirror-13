from lxml import etree

from healthvaultlib.utils.xmlutils import XmlUtils
from healthvaultlib.itemtypes.healthrecorditem import HealthRecordItem


class BloodPressure(HealthRecordItem):

    def __init__(self, thing_xml=None):
        super(BloodPressure, self).__init__()
        self.type_id = 'ca3c57f4-f4c1-4e15-be67-0a3caf5414ed'
        if thing_xml is not None:
            self.thing_xml = thing_xml
            self.parse_thing()

    def __str__(self):
        return 'BloodPressure'

    def parse_thing(self):
        super(BloodPressure, self).parse_thing()
        xmlutils = XmlUtils(self.thing_xml)

    def write_xml(self):
        thing = super(BloodPressure, self).write_xml()
        data_xml = etree.Element('data-xml')
        bloodpressure = etree.Element('bloodpressure')

        data_xml.append(bloodpressure)
        thing.append(data_xml)
        return thing
