from lxml import etree

from healthvaultlib.utils.xmlutils import XmlUtils
from healthvaultlib.itemtypes.healthrecorditem import HealthRecordItem


class Concern(HealthRecordItem):

    def __init__(self, thing_xml=None):
        super(Concern, self).__init__()
        self.type_id = 'aea2e8f2-11dd-4a7d-ab43-1d58764ebc19'
        if thing_xml is not None:
            self.thing_xml = thing_xml
            self.parse_thing()

    def __str__(self):
        return 'Concern'

    def parse_thing(self):
        super(Concern, self).parse_thing()
        xmlutils = XmlUtils(self.thing_xml)

    def write_xml(self):
        thing = super(Concern, self).write_xml()
        data_xml = etree.Element('data-xml')
        concern = etree.Element('concern')

        data_xml.append(concern)
        thing.append(data_xml)
        return thing
