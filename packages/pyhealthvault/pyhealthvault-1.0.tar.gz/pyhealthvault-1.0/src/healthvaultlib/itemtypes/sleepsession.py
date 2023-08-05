from lxml import etree

from healthvaultlib.utils.xmlutils import XmlUtils
from healthvaultlib.itemtypes.healthrecorditem import HealthRecordItem


class SleepSession(HealthRecordItem):

    def __init__(self, thing_xml=None):
        super(SleepSession, self).__init__()
        self.type_id = '11c52484-7f1a-11db-aeac-87d355d89593'
        if thing_xml is not None:
            self.thing_xml = thing_xml
            self.parse_thing()

    def __str__(self):
        return 'SleepSession'

    def parse_thing(self):
        super(SleepSession, self).parse_thing()
        xmlutils = XmlUtils(self.thing_xml)

    def write_xml(self):
        thing = super(SleepSession, self).write_xml()
        data_xml = etree.Element('data-xml')
        sleepsession = etree.Element('sleepsession')

        data_xml.append(sleepsession)
        thing.append(data_xml)
        return thing
