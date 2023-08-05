from lxml import etree

from healthvaultlib.utils.xmlutils import XmlUtils
from healthvaultlib.itemtypes.healthrecorditem import HealthRecordItem


class DailyMedicationUsage(HealthRecordItem):

    def __init__(self, thing_xml=None):
        super(DailyMedicationUsage, self).__init__()
        self.type_id = 'a9a76456-0357-493e-b840-598bbb9483fd'
        if thing_xml is not None:
            self.thing_xml = thing_xml
            self.parse_thing()

    def __str__(self):
        return 'DailyMedicationUsage'

    def parse_thing(self):
        super(DailyMedicationUsage, self).parse_thing()
        xmlutils = XmlUtils(self.thing_xml)

    def write_xml(self):
        thing = super(DailyMedicationUsage, self).write_xml()
        data_xml = etree.Element('data-xml')
        dailymedicationusage = etree.Element('dailymedicationusage')

        data_xml.append(dailymedicationusage)
        thing.append(data_xml)
        return thing
