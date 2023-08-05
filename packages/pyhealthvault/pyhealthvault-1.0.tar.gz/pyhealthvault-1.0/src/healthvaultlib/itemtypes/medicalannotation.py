from lxml import etree

from healthvaultlib.utils.xmlutils import XmlUtils
from healthvaultlib.itemtypes.healthrecorditem import HealthRecordItem


class MedicalAnnotation(HealthRecordItem):

    def __init__(self, thing_xml=None):
        super(MedicalAnnotation, self).__init__()
        self.type_id = '7ab3e662-cc5b-4be2-bf38-78f8aad5b161'
        if thing_xml is not None:
            self.thing_xml = thing_xml
            self.parse_thing()

    def __str__(self):
        return 'MedicalAnnotation'

    def parse_thing(self):
        super(MedicalAnnotation, self).parse_thing()
        xmlutils = XmlUtils(self.thing_xml)

    def write_xml(self):
        thing = super(MedicalAnnotation, self).write_xml()
        data_xml = etree.Element('data-xml')
        medicalannotation = etree.Element('medicalannotation')

        data_xml.append(medicalannotation)
        thing.append(data_xml)
        return thing
