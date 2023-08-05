from lxml import etree

from healthvaultlib.utils.xmlutils import XmlUtils
from healthvaultlib.itemtypes.healthrecorditem import HealthRecordItem


class BloodOxygenSaturation(HealthRecordItem):

    def __init__(self, thing_xml=None):
        super(BloodOxygenSaturation, self).__init__()
        self.type_id = '3a54f95f-03d8-4f62-815f-f691fc94a500'
        if thing_xml is not None:
            self.thing_xml = thing_xml
            self.parse_thing()

    def __str__(self):
        return 'BloodOxygenSaturation'

    def parse_thing(self):
        super(BloodOxygenSaturation, self).parse_thing()
        xmlutils = XmlUtils(self.thing_xml)

    def write_xml(self):
        thing = super(BloodOxygenSaturation, self).write_xml()
        data_xml = etree.Element('data-xml')
        bloodoxygensaturation = etree.Element('bloodoxygensaturation')

        data_xml.append(bloodoxygensaturation)
        thing.append(data_xml)
        return thing
