from lxml import etree

from healthvaultlib.utils.xmlutils import XmlUtils
from healthvaultlib.itemtypes.healthrecorditem import HealthRecordItem


class AerobicProfile(HealthRecordItem):

    def __init__(self, thing_xml=None):
        super(AerobicProfile, self).__init__()
        self.type_id = '7b2ea78c-4b78-4f75-a6a7-5396fe38b09a'
        if thing_xml is not None:
            self.thing_xml = thing_xml
            self.parse_thing()

    def __str__(self):
        return 'AerobicProfile'

    def parse_thing(self):
        super(AerobicProfile, self).parse_thing()
        xmlutils = XmlUtils(self.thing_xml)

    def write_xml(self):
        thing = super(AerobicProfile, self).write_xml()
        data_xml = etree.Element('data-xml')
        aerobicprofile = etree.Element('aerobicprofile')

        data_xml.append(aerobicprofile)
        thing.append(data_xml)
        return thing
