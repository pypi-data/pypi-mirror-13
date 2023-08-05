from lxml import etree

from healthvaultlib.utils.xmlutils import XmlUtils
from healthvaultlib.itemtypes.healthrecorditem import HealthRecordItem


class AsthmaInhaler(HealthRecordItem):

    def __init__(self, thing_xml=None):
        super(AsthmaInhaler, self).__init__()
        self.type_id = 'ff9ce191-2096-47d8-9300-5469a9883746'
        if thing_xml is not None:
            self.thing_xml = thing_xml
            self.parse_thing()

    def __str__(self):
        return 'AsthmaInhaler'

    def parse_thing(self):
        super(AsthmaInhaler, self).parse_thing()
        xmlutils = XmlUtils(self.thing_xml)

    def write_xml(self):
        thing = super(AsthmaInhaler, self).write_xml()
        data_xml = etree.Element('data-xml')
        asthmainhaler = etree.Element('asthmainhaler')

        data_xml.append(asthmainhaler)
        thing.append(data_xml)
        return thing
