from lxml import etree

from healthvaultlib.utils.xmlutils import XmlUtils
from healthvaultlib.itemtypes.healthrecorditem import HealthRecordItem


class Appointment(HealthRecordItem):

    def __init__(self, thing_xml=None):
        super(Appointment, self).__init__()
        self.type_id = '4b18aeb6-5f01-444c-8c70-dbf13a2f510b'
        if thing_xml is not None:
            self.thing_xml = thing_xml
            self.parse_thing()

    def __str__(self):
        return 'Appointment'

    def parse_thing(self):
        super(Appointment, self).parse_thing()
        xmlutils = XmlUtils(self.thing_xml)

    def write_xml(self):
        thing = super(Appointment, self).write_xml()
        data_xml = etree.Element('data-xml')
        appointment = etree.Element('appointment')

        data_xml.append(appointment)
        thing.append(data_xml)
        return thing
