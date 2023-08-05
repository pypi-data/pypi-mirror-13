from lxml import etree

from healthvaultlib.utils.xmlutils import XmlUtils
from healthvaultlib.itemtypes.healthrecorditem import HealthRecordItem


class HealthcareProxy(HealthRecordItem):

    def __init__(self, thing_xml=None):
        super(HealthcareProxy, self).__init__()
        self.type_id = '7ea47715-cba4-47f0-99d2-eb0a9fb4a85c'
        if thing_xml is not None:
            self.thing_xml = thing_xml
            self.parse_thing()

    def __str__(self):
        return 'HealthcareProxy'

    def parse_thing(self):
        super(HealthcareProxy, self).parse_thing()
        xmlutils = XmlUtils(self.thing_xml)

    def write_xml(self):
        thing = super(HealthcareProxy, self).write_xml()
        data_xml = etree.Element('data-xml')
        healthcareproxy = etree.Element('healthcareproxy')

        data_xml.append(healthcareproxy)
        thing.append(data_xml)
        return thing
