from lxml import etree

from healthvaultlib.utils.xmlutils import XmlUtils
from healthvaultlib.itemtypes.healthrecorditem import HealthRecordItem


class VitalSigns(HealthRecordItem):

    def __init__(self, thing_xml=None):
        super(VitalSigns, self).__init__()
        self.type_id = '73822612-c15f-4b49-9e65-6af369e55c65'
        if thing_xml is not None:
            self.thing_xml = thing_xml
            self.parse_thing()

    def __str__(self):
        return 'VitalSigns'

    def parse_thing(self):
        super(VitalSigns, self).parse_thing()
        xmlutils = XmlUtils(self.thing_xml)

    def write_xml(self):
        thing = super(VitalSigns, self).write_xml()
        data_xml = etree.Element('data-xml')
        vitalsigns = etree.Element('vitalsigns')

        data_xml.append(vitalsigns)
        thing.append(data_xml)
        return thing
