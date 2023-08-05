from lxml import etree

from healthvaultlib.utils.xmlutils import XmlUtils
from healthvaultlib.itemtypes.healthrecorditem import HealthRecordItem


class InsulinInjection(HealthRecordItem):

    def __init__(self, thing_xml=None):
        super(InsulinInjection, self).__init__()
        self.type_id = '3b3c053b-b1fe-4e11-9e22-d4b480de74e8'
        if thing_xml is not None:
            self.thing_xml = thing_xml
            self.parse_thing()

    def __str__(self):
        return 'InsulinInjection'

    def parse_thing(self):
        super(InsulinInjection, self).parse_thing()
        xmlutils = XmlUtils(self.thing_xml)

    def write_xml(self):
        thing = super(InsulinInjection, self).write_xml()
        data_xml = etree.Element('data-xml')
        insulininjection = etree.Element('insulininjection')

        data_xml.append(insulininjection)
        thing.append(data_xml)
        return thing
