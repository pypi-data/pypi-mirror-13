from lxml import etree

from healthvaultlib.utils.xmlutils import XmlUtils
from healthvaultlib.itemtypes.healthrecorditem import HealthRecordItem


class Message(HealthRecordItem):

    def __init__(self, thing_xml=None):
        super(Message, self).__init__()
        self.type_id = '72dc49e1-1486-4634-b651-ef560ed051e5'
        if thing_xml is not None:
            self.thing_xml = thing_xml
            self.parse_thing()

    def __str__(self):
        return 'Message'

    def parse_thing(self):
        super(Message, self).parse_thing()
        xmlutils = XmlUtils(self.thing_xml)

    def write_xml(self):
        thing = super(Message, self).write_xml()
        data_xml = etree.Element('data-xml')
        message = etree.Element('message')

        data_xml.append(message)
        thing.append(data_xml)
        return thing
