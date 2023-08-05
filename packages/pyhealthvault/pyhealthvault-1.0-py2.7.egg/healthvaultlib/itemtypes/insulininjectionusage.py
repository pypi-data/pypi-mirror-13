from lxml import etree

from healthvaultlib.utils.xmlutils import XmlUtils
from healthvaultlib.itemtypes.healthrecorditem import HealthRecordItem


class InsulinInjectionUsage(HealthRecordItem):

    def __init__(self, thing_xml=None):
        super(InsulinInjectionUsage, self).__init__()
        self.type_id = '184166be-8adb-4d9c-8162-c403040e31ad'
        if thing_xml is not None:
            self.thing_xml = thing_xml
            self.parse_thing()

    def __str__(self):
        return 'InsulinInjectionUsage'

    def parse_thing(self):
        super(InsulinInjectionUsage, self).parse_thing()
        xmlutils = XmlUtils(self.thing_xml)

    def write_xml(self):
        thing = super(InsulinInjectionUsage, self).write_xml()
        data_xml = etree.Element('data-xml')
        insulininjectionusage = etree.Element('insulininjectionusage')

        data_xml.append(insulininjectionusage)
        thing.append(data_xml)
        return thing
