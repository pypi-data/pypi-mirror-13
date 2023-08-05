from lxml import etree

from healthvaultlib.utils.xmlutils import XmlUtils
from healthvaultlib.itemtypes.healthrecorditem import HealthRecordItem


class Weight(HealthRecordItem):

    def __init__(self, thing_xml=None):
        super(Weight, self).__init__()
        self.type_id = '3d34d87e-7fc1-4153-800f-f56592cb0d17'
        if thing_xml is not None:
            self.thing_xml = thing_xml
            self.parse_thing()

    def __str__(self):
        return 'Weight'

    def parse_thing(self):
        super(Weight, self).parse_thing()
        xmlutils = XmlUtils(self.thing_xml)

    def write_xml(self):
        thing = super(Weight, self).write_xml()
        data_xml = etree.Element('data-xml')
        weight = etree.Element('weight')

        data_xml.append(weight)
        thing.append(data_xml)
        return thing
