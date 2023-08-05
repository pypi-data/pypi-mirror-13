from lxml import etree

from healthvaultlib.utils.xmlutils import XmlUtils
from healthvaultlib.itemtypes.healthrecorditem import HealthRecordItem


class File(HealthRecordItem):

    def __init__(self, thing_xml=None):
        super(File, self).__init__()
        self.type_id = 'bd0403c5-4ae2-4b0e-a8db-1888678e4528'
        if thing_xml is not None:
            self.thing_xml = thing_xml
            self.parse_thing()

    def __str__(self):
        return 'File'

    def parse_thing(self):
        super(File, self).parse_thing()
        xmlutils = XmlUtils(self.thing_xml)

    def write_xml(self):
        thing = super(File, self).write_xml()
        data_xml = etree.Element('data-xml')
        file = etree.Element('file')

        data_xml.append(file)
        thing.append(data_xml)
        return thing
