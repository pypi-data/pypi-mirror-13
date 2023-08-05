from lxml import etree

from healthvaultlib.utils.xmlutils import XmlUtils
from healthvaultlib.itemtypes.healthrecorditem import HealthRecordItem


class Medication(HealthRecordItem):

    def __init__(self, thing_xml=None):
        super(Medication, self).__init__()
        self.type_id = '30cafccc-047d-4288-94ef-643571f7919d'
        if thing_xml is not None:
            self.thing_xml = thing_xml
            self.parse_thing()

    def __str__(self):
        return 'Medication'

    def parse_thing(self):
        super(Medication, self).parse_thing()
        xmlutils = XmlUtils(self.thing_xml)

    def write_xml(self):
        thing = super(Medication, self).write_xml()
        data_xml = etree.Element('data-xml')
        medication = etree.Element('medication')

        data_xml.append(medication)
        thing.append(data_xml)
        return thing
