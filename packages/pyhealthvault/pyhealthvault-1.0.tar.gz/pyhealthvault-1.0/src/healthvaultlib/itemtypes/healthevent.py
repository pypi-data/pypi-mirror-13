from lxml import etree

from healthvaultlib.utils.xmlutils import XmlUtils
from healthvaultlib.itemtypes.healthrecorditem import HealthRecordItem


class HealthEvent(HealthRecordItem):

    def __init__(self, thing_xml=None):
        super(HealthEvent, self).__init__()
        self.type_id = '1572af76-1653-4c39-9683-9f9ca6584ba3'
        if thing_xml is not None:
            self.thing_xml = thing_xml
            self.parse_thing()

    def __str__(self):
        return 'HealthEvent'

    def parse_thing(self):
        super(HealthEvent, self).parse_thing()
        xmlutils = XmlUtils(self.thing_xml)

    def write_xml(self):
        thing = super(HealthEvent, self).write_xml()
        data_xml = etree.Element('data-xml')
        healthevent = etree.Element('healthevent')

        data_xml.append(healthevent)
        thing.append(data_xml)
        return thing
