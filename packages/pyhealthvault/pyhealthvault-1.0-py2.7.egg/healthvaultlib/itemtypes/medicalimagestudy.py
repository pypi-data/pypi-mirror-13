from lxml import etree

from healthvaultlib.utils.xmlutils import XmlUtils
from healthvaultlib.itemtypes.healthrecorditem import HealthRecordItem


class MedicalImageStudy(HealthRecordItem):

    def __init__(self, thing_xml=None):
        super(MedicalImageStudy, self).__init__()
        self.type_id = 'cdfc0a9b-6d3b-4d16-afa8-02b86d621a8d'
        if thing_xml is not None:
            self.thing_xml = thing_xml
            self.parse_thing()

    def __str__(self):
        return 'MedicalImageStudy'

    def parse_thing(self):
        super(MedicalImageStudy, self).parse_thing()
        xmlutils = XmlUtils(self.thing_xml)

    def write_xml(self):
        thing = super(MedicalImageStudy, self).write_xml()
        data_xml = etree.Element('data-xml')
        medicalimagestudy = etree.Element('medicalimagestudy')

        data_xml.append(medicalimagestudy)
        thing.append(data_xml)
        return thing
