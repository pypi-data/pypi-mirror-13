from lxml import etree

from healthvaultlib.utils.xmlutils import XmlUtils
from healthvaultlib.itemtypes.healthrecorditem import HealthRecordItem


class PasswordprotectedPackage(HealthRecordItem):

    def __init__(self, thing_xml=None):
        super(PasswordprotectedPackage, self).__init__()
        self.type_id = 'c9287326-bb43-4194-858c-8b60768f000f'
        if thing_xml is not None:
            self.thing_xml = thing_xml
            self.parse_thing()

    def __str__(self):
        return 'PasswordprotectedPackage'

    def parse_thing(self):
        super(PasswordprotectedPackage, self).parse_thing()
        xmlutils = XmlUtils(self.thing_xml)

    def write_xml(self):
        thing = super(PasswordprotectedPackage, self).write_xml()
        data_xml = etree.Element('data-xml')
        passwordprotectedpackage = etree.Element('passwordprotectedpackage')

        data_xml.append(passwordprotectedpackage)
        thing.append(data_xml)
        return thing
