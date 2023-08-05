from lxml import etree

from healthvaultlib.utils.xmlutils import XmlUtils
from healthvaultlib.itemtypes.healthrecorditem import HealthRecordItem


class Cholesterol(HealthRecordItem):

    def __init__(self, thing_xml=None):
        super(Cholesterol, self).__init__()
        self.type_id = '98f76958-e34f-459b-a760-83c1699add38'
        if thing_xml is not None:
            self.thing_xml = thing_xml
            self.parse_thing()

    def __str__(self):
        return 'Cholesterol'

    def parse_thing(self):
        super(Cholesterol, self).parse_thing()
        xmlutils = XmlUtils(self.thing_xml)

    def write_xml(self):
        thing = super(Cholesterol, self).write_xml()
        data_xml = etree.Element('data-xml')
        cholesterol = etree.Element('cholesterol')

        data_xml.append(cholesterol)
        thing.append(data_xml)
        return thing
