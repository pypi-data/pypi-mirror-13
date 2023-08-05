from lxml import etree

from healthvaultlib.utils.xmlutils import XmlUtils
from healthvaultlib.itemtypes.healthrecorditem import HealthRecordItem


class PersonalDemographicInformation(HealthRecordItem):

    def __init__(self, thing_xml=None):
        super(PersonalDemographicInformation, self).__init__()
        self.type_id = '92ba621e-66b3-4a01-bd73-74844aed4f5b'
        if thing_xml is not None:
            self.thing_xml = thing_xml
            self.parse_thing()

    def __str__(self):
        return 'PersonalDemographicInformation'

    def parse_thing(self):
        super(PersonalDemographicInformation, self).parse_thing()
        xmlutils = XmlUtils(self.thing_xml)

    def write_xml(self):
        thing = super(PersonalDemographicInformation, self).write_xml()
        data_xml = etree.Element('data-xml')
        personaldemographicinformation = etree.Element('personaldemographicinformation')

        data_xml.append(personaldemographicinformation)
        thing.append(data_xml)
        return thing
