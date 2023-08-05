from lxml import etree

from healthvaultlib.utils.xmlutils import XmlUtils
from healthvaultlib.itemtypes.healthrecorditem import HealthRecordItem


class Allergy(HealthRecordItem):

    def __init__(self, thing_xml=None):
        super(Allergy, self).__init__()
        self.type_id = '52bf9104-2c5e-4f1f-a66d-552ebcc53df7'
        if thing_xml is not None:
            self.thing_xml = thing_xml
            self.parse_thing()

    def __str__(self):
        return 'Allergy'

    def parse_thing(self):
        super(Allergy, self).parse_thing()
        xmlutils = XmlUtils(self.thing_xml)

    def write_xml(self):
        thing = super(Allergy, self).write_xml()
        data_xml = etree.Element('data-xml')
        allergy = etree.Element('allergy')

        data_xml.append(allergy)
        thing.append(data_xml)
        return thing
