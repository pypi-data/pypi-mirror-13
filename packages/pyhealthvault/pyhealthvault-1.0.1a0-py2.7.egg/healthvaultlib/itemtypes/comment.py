from lxml import etree

from healthvaultlib.utils.xmlutils import XmlUtils
from healthvaultlib.itemtypes.healthrecorditem import HealthRecordItem


class Comment(HealthRecordItem):

    def __init__(self, thing_xml=None):
        super(Comment, self).__init__()
        self.type_id = '9f4e0fcd-10d7-416d-855a-90514ce2016b'
        if thing_xml is not None:
            self.thing_xml = thing_xml
            self.parse_thing()

    def __str__(self):
        return 'Comment'

    def parse_thing(self):
        super(Comment, self).parse_thing()
        xmlutils = XmlUtils(self.thing_xml)

    def write_xml(self):
        thing = super(Comment, self).write_xml()
        data_xml = etree.Element('data-xml')
        comment = etree.Element('comment')

        data_xml.append(comment)
        thing.append(data_xml)
        return thing
