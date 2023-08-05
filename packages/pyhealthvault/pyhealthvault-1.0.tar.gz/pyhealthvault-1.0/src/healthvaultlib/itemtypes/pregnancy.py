from lxml import etree

from healthvaultlib.utils.xmlutils import XmlUtils
from healthvaultlib.itemtypes.healthrecorditem import HealthRecordItem


class Pregnancy(HealthRecordItem):

    def __init__(self, thing_xml=None):
        super(Pregnancy, self).__init__()
        self.type_id = '46d485cf-2b84-429d-9159-83152ba801f4'
        if thing_xml is not None:
            self.thing_xml = thing_xml
            self.parse_thing()

    def __str__(self):
        return 'Pregnancy'

    def parse_thing(self):
        super(Pregnancy, self).parse_thing()
        xmlutils = XmlUtils(self.thing_xml)

    def write_xml(self):
        thing = super(Pregnancy, self).write_xml()
        data_xml = etree.Element('data-xml')
        pregnancy = etree.Element('pregnancy')

        data_xml.append(pregnancy)
        thing.append(data_xml)
        return thing
