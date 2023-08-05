from lxml import etree

from healthvaultlib.utils.xmlutils import XmlUtils
from healthvaultlib.itemtypes.healthrecorditem import HealthRecordItem


class GroupMembership(HealthRecordItem):

    def __init__(self, thing_xml=None):
        super(GroupMembership, self).__init__()
        self.type_id = '66ac44c7-1d60-4e95-bb5b-d21490e91057'
        if thing_xml is not None:
            self.thing_xml = thing_xml
            self.parse_thing()

    def __str__(self):
        return 'GroupMembership'

    def parse_thing(self):
        super(GroupMembership, self).parse_thing()
        xmlutils = XmlUtils(self.thing_xml)

    def write_xml(self):
        thing = super(GroupMembership, self).write_xml()
        data_xml = etree.Element('data-xml')
        groupmembership = etree.Element('groupmembership')

        data_xml.append(groupmembership)
        thing.append(data_xml)
        return thing
