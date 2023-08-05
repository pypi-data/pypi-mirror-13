from lxml import etree

from healthvaultlib.utils.xmlutils import XmlUtils
from healthvaultlib.itemtypes.healthrecorditem import HealthRecordItem


class AllergicEpisode(HealthRecordItem):

    def __init__(self, thing_xml=None):
        super(AllergicEpisode, self).__init__()
        self.type_id = 'd65ad514-c492-4b59-bd05-f3f6cb43ceb3'
        if thing_xml is not None:
            self.thing_xml = thing_xml
            self.parse_thing()

    def __str__(self):
        return 'AllergicEpisode'

    def parse_thing(self):
        super(AllergicEpisode, self).parse_thing()
        xmlutils = XmlUtils(self.thing_xml)

    def write_xml(self):
        thing = super(AllergicEpisode, self).write_xml()
        data_xml = etree.Element('data-xml')
        allergicepisode = etree.Element('allergicepisode')

        data_xml.append(allergicepisode)
        thing.append(data_xml)
        return thing
