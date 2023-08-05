from lxml import etree

from healthvaultlib.utils.xmlutils import XmlUtils
from healthvaultlib.itemtypes.healthrecorditem import HealthRecordItem


class PeakFlow(HealthRecordItem):

    def __init__(self, thing_xml=None):
        super(PeakFlow, self).__init__()
        self.type_id = '5d8419af-90f0-4875-a370-0f881c18f6b3'
        if thing_xml is not None:
            self.thing_xml = thing_xml
            self.parse_thing()

    def __str__(self):
        return 'PeakFlow'

    def parse_thing(self):
        super(PeakFlow, self).parse_thing()
        xmlutils = XmlUtils(self.thing_xml)

    def write_xml(self):
        thing = super(PeakFlow, self).write_xml()
        data_xml = etree.Element('data-xml')
        peakflow = etree.Element('peakflow')

        data_xml.append(peakflow)
        thing.append(data_xml)
        return thing
