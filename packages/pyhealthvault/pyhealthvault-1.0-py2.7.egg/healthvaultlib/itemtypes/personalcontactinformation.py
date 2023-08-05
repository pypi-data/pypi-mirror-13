from lxml import etree

from healthvaultlib.utils.xmlutils import XmlUtils
from healthvaultlib.itemtypes.healthrecorditem import HealthRecordItem


class PersonalContactInformation(HealthRecordItem):

    def __init__(self, thing_xml=None):
        super(PersonalContactInformation, self).__init__()
        self.type_id = '162dd12d-9859-4a66-b75f-96760d67072b'
        if thing_xml is not None:
            self.thing_xml = thing_xml
            self.parse_thing()

    def __str__(self):
        return 'PersonalContactInformation'

    def parse_thing(self):
        super(PersonalContactInformation, self).parse_thing()
        xmlutils = XmlUtils(self.thing_xml)

    def write_xml(self):
        thing = super(PersonalContactInformation, self).write_xml()
        data_xml = etree.Element('data-xml')
        personalcontactinformation = etree.Element('personalcontactinformation')

        data_xml.append(personalcontactinformation)
        thing.append(data_xml)
        return thing
