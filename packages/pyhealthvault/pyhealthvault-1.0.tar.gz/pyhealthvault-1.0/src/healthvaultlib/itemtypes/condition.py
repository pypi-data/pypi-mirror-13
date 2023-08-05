from lxml import etree

from healthvaultlib.utils.xmlutils import XmlUtils
from healthvaultlib.itemtypes.healthrecorditem import HealthRecordItem


class Condition(HealthRecordItem):

    def __init__(self, thing_xml=None):
        super(Condition, self).__init__()
        self.type_id = '7ea7a1f9-880b-4bd4-b593-f5660f20eda8'
        if thing_xml is not None:
            self.thing_xml = thing_xml
            self.parse_thing()

    def __str__(self):
        return 'Condition'

    def parse_thing(self):
        super(Condition, self).parse_thing()
        xmlutils = XmlUtils(self.thing_xml)

    def write_xml(self):
        thing = super(Condition, self).write_xml()
        data_xml = etree.Element('data-xml')
        condition = etree.Element('condition')

        data_xml.append(condition)
        thing.append(data_xml)
        return thing
