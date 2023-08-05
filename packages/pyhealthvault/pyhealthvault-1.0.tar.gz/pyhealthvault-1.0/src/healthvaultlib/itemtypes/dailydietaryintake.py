from lxml import etree

from healthvaultlib.utils.xmlutils import XmlUtils
from healthvaultlib.itemtypes.healthrecorditem import HealthRecordItem


class DailyDietaryIntake(HealthRecordItem):

    def __init__(self, thing_xml=None):
        super(DailyDietaryIntake, self).__init__()
        self.type_id = '9c29c6b9-f40e-44ff-b24e-fba6f3074638'
        if thing_xml is not None:
            self.thing_xml = thing_xml
            self.parse_thing()

    def __str__(self):
        return 'DailyDietaryIntake'

    def parse_thing(self):
        super(DailyDietaryIntake, self).parse_thing()
        xmlutils = XmlUtils(self.thing_xml)

    def write_xml(self):
        thing = super(DailyDietaryIntake, self).write_xml()
        data_xml = etree.Element('data-xml')
        dailydietaryintake = etree.Element('dailydietaryintake')

        data_xml.append(dailydietaryintake)
        thing.append(data_xml)
        return thing
