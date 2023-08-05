from lxml import etree

from healthvaultlib.utils.xmlutils import XmlUtils
from healthvaultlib.itemtypes.healthrecorditem import HealthRecordItem


class Menstruation(HealthRecordItem):

    def __init__(self, thing_xml=None):
        super(Menstruation, self).__init__()
        self.type_id = 'caff3ff3-812f-44b1-9c9f-c1af13167705'
        if thing_xml is not None:
            self.thing_xml = thing_xml
            self.parse_thing()

    def __str__(self):
        return 'Menstruation'

    def parse_thing(self):
        super(Menstruation, self).parse_thing()
        xmlutils = XmlUtils(self.thing_xml)

    def write_xml(self):
        thing = super(Menstruation, self).write_xml()
        data_xml = etree.Element('data-xml')
        menstruation = etree.Element('menstruation')

        data_xml.append(menstruation)
        thing.append(data_xml)
        return thing
