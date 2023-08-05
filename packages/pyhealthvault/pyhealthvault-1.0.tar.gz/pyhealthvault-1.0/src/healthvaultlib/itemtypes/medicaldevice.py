from lxml import etree

from healthvaultlib.utils.xmlutils import XmlUtils
from healthvaultlib.itemtypes.healthrecorditem import HealthRecordItem


class MedicalDevice(HealthRecordItem):

    def __init__(self, thing_xml=None):
        super(MedicalDevice, self).__init__()
        self.type_id = 'ef9cf8d5-6c0b-4292-997f-4047240bc7be'
        if thing_xml is not None:
            self.thing_xml = thing_xml
            self.parse_thing()

    def __str__(self):
        return 'MedicalDevice'

    def parse_thing(self):
        super(MedicalDevice, self).parse_thing()
        xmlutils = XmlUtils(self.thing_xml)

    def write_xml(self):
        thing = super(MedicalDevice, self).write_xml()
        data_xml = etree.Element('data-xml')
        medicaldevice = etree.Element('medicaldevice')

        data_xml.append(medicaldevice)
        thing.append(data_xml)
        return thing
