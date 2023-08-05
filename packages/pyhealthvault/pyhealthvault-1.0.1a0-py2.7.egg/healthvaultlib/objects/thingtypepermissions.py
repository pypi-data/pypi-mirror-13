from healthvaultlib.utils.xmlutils import XmlUtils
from healthvaultlib.objects.permission import Permission


class ThingTypePermissions:

    def __init__(self, permission_xml=None):
        self.thing_type_id = ''
        self.online_access_permissions = None
        self.offline_access_permissions = None
        self.other_settings = {}

        if permission_xml is not None:
            self.parse_xml(permission_xml)

    def parse_xml(self, thing_type_permission_xml):
        xmlutils = XmlUtils(thing_type_permission_xml)
        self.thing_type_id = xmlutils.get_string_by_xpath('thing-type-id/text()')
        if thing_type_permission_xml.xpath('online-access-permissions') != []:
            self.online_access_permissions = Permission(thing_type_permission_xml.xpath('online-access-permissions')[0])
        if thing_type_permission_xml.xpath('offline-access-permissions') != []:
            self.offline_access_permissions = Permission(thing_type_permission_xml.xpath('offline-access-permissions')[0])
