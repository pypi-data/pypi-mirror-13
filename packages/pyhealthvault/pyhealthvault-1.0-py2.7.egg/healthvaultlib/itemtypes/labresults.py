from lxml import etree

from healthvaultlib.utils.xmlutils import XmlUtils
from healthvaultlib.itemtypes.healthrecorditem import HealthRecordItem


class LabResults(HealthRecordItem):

    def __init__(self, thing_xml=None):
        super(LabResults, self).__init__()
        self.type_id = '5800eab5-a8c2-482a-a4d6-f1db25ae08c3'
        if thing_xml is not None:
            self.thing_xml = thing_xml
            self.parse_thing()

    def __str__(self):
        return 'LabResults'

    def parse_thing(self):
        super(LabResults, self).parse_thing()
        xmlutils = XmlUtils(self.thing_xml)

    def write_xml(self):
        thing = super(LabResults, self).write_xml()
        data_xml = etree.Element('data-xml')
        labresults = etree.Element('labresults')

        data_xml.append(labresults)
        thing.append(data_xml)
        return thing
