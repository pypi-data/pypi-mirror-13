from lxml import etree

from healthvaultlib.utils.xmlutils import XmlUtils
from healthvaultlib.itemtypes.healthrecorditem import HealthRecordItem


class HealthAssessment(HealthRecordItem):

    def __init__(self, thing_xml=None):
        super(HealthAssessment, self).__init__()
        self.type_id = '58fd8ac4-6c47-41a3-94b2-478401f0e26c'
        if thing_xml is not None:
            self.thing_xml = thing_xml
            self.parse_thing()

    def __str__(self):
        return 'HealthAssessment'

    def parse_thing(self):
        super(HealthAssessment, self).parse_thing()
        xmlutils = XmlUtils(self.thing_xml)

    def write_xml(self):
        thing = super(HealthAssessment, self).write_xml()
        data_xml = etree.Element('data-xml')
        healthassessment = etree.Element('healthassessment')

        data_xml.append(healthassessment)
        thing.append(data_xml)
        return thing
