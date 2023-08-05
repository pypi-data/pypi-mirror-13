from lxml import etree

from healthvaultlib.utils.xmlutils import XmlUtils
from healthvaultlib.itemtypes.healthrecorditem import HealthRecordItem


class Immunization(HealthRecordItem):

    def __init__(self, thing_xml=None):
        super(Immunization, self).__init__()
        self.type_id = 'cd3587b5-b6e1-4565-ab3b-1c3ad45eb04f'
        if thing_xml is not None:
            self.thing_xml = thing_xml
            self.parse_thing()

    def __str__(self):
        return 'Immunization'

    def parse_thing(self):
        super(Immunization, self).parse_thing()
        xmlutils = XmlUtils(self.thing_xml)

    def write_xml(self):
        thing = super(Immunization, self).write_xml()
        data_xml = etree.Element('data-xml')
        immunization = etree.Element('immunization')

        data_xml.append(immunization)
        thing.append(data_xml)
        return thing
