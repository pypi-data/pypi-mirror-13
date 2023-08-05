from lxml import etree

from healthvaultlib.utils.xmlutils import XmlUtils
from healthvaultlib.itemtypes.healthrecorditem import HealthRecordItem


class AsthmaInhalerUsage(HealthRecordItem):

    def __init__(self, thing_xml=None):
        super(AsthmaInhalerUsage, self).__init__()
        self.type_id = '03efe378-976a-42f8-ae1e-507c497a8c6d'
        if thing_xml is not None:
            self.thing_xml = thing_xml
            self.parse_thing()

    def __str__(self):
        return 'AsthmaInhalerUsage'

    def parse_thing(self):
        super(AsthmaInhalerUsage, self).parse_thing()
        xmlutils = XmlUtils(self.thing_xml)

    def write_xml(self):
        thing = super(AsthmaInhalerUsage, self).write_xml()
        data_xml = etree.Element('data-xml')
        asthmainhalerusage = etree.Element('asthmainhalerusage')

        data_xml.append(asthmainhalerusage)
        thing.append(data_xml)
        return thing
