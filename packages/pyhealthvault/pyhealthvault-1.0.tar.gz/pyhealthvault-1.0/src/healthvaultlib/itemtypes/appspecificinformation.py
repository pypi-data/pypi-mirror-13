from lxml import etree

from healthvaultlib.utils.xmlutils import XmlUtils
from healthvaultlib.itemtypes.healthrecorditem import HealthRecordItem


class AppspecificInformation(HealthRecordItem):

    def __init__(self, thing_xml=None):
        super(AppspecificInformation, self).__init__()
        self.type_id = 'a5033c9d-08cf-4204-9bd3-cb412ce39fc0'
        if thing_xml is not None:
            self.thing_xml = thing_xml
            self.parse_thing()

    def __str__(self):
        return 'AppspecificInformation'

    def parse_thing(self):
        super(AppspecificInformation, self).parse_thing()
        xmlutils = XmlUtils(self.thing_xml)

    def write_xml(self):
        thing = super(AppspecificInformation, self).write_xml()
        data_xml = etree.Element('data-xml')
        appspecificinformation = etree.Element('appspecificinformation')

        data_xml.append(appspecificinformation)
        thing.append(data_xml)
        return thing
