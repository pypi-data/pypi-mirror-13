from lxml import etree

from healthvaultlib.utils.xmlutils import XmlUtils
from healthvaultlib.itemtypes.healthrecorditem import HealthRecordItem


class GroupMembershipActivity(HealthRecordItem):

    def __init__(self, thing_xml=None):
        super(GroupMembershipActivity, self).__init__()
        self.type_id = 'e75fa095-31ed-4b30-b5f7-463963b5e734'
        if thing_xml is not None:
            self.thing_xml = thing_xml
            self.parse_thing()

    def __str__(self):
        return 'GroupMembershipActivity'

    def parse_thing(self):
        super(GroupMembershipActivity, self).parse_thing()
        xmlutils = XmlUtils(self.thing_xml)

    def write_xml(self):
        thing = super(GroupMembershipActivity, self).write_xml()
        data_xml = etree.Element('data-xml')
        groupmembershipactivity = etree.Element('groupmembershipactivity')

        data_xml.append(groupmembershipactivity)
        thing.append(data_xml)
        return thing
