from lxml import etree

from healthvaultlib.utils.xmlutils import XmlUtils
from healthvaultlib.itemtypes.healthrecorditem import HealthRecordItem


class EducationMydataFile(HealthRecordItem):

    def __init__(self, thing_xml=None):
        super(EducationMydataFile, self).__init__()
        self.type_id = '0aa6a4c7-cef5-46ea-970e-206c8402dccb'
        if thing_xml is not None:
            self.thing_xml = thing_xml
            self.parse_thing()

    def __str__(self):
        return 'EducationMydataFile'

    def parse_thing(self):
        super(EducationMydataFile, self).parse_thing()
        xmlutils = XmlUtils(self.thing_xml)

    def write_xml(self):
        thing = super(EducationMydataFile, self).write_xml()
        data_xml = etree.Element('data-xml')
        educationmydatafile = etree.Element('educationmydatafile')

        data_xml.append(educationmydatafile)
        thing.append(data_xml)
        return thing
