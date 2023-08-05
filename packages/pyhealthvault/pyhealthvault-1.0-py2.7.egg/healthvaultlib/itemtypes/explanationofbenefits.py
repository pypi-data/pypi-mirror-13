from lxml import etree

from healthvaultlib.utils.xmlutils import XmlUtils
from healthvaultlib.itemtypes.healthrecorditem import HealthRecordItem


class ExplanationOfBenefits(HealthRecordItem):

    def __init__(self, thing_xml=None):
        super(ExplanationOfBenefits, self).__init__()
        self.type_id = '356fbba9-e0c9-4f4f-b0d9-4594f2490d2f'
        if thing_xml is not None:
            self.thing_xml = thing_xml
            self.parse_thing()

    def __str__(self):
        return 'ExplanationOfBenefits'

    def parse_thing(self):
        super(ExplanationOfBenefits, self).parse_thing()
        xmlutils = XmlUtils(self.thing_xml)

    def write_xml(self):
        thing = super(ExplanationOfBenefits, self).write_xml()
        data_xml = etree.Element('data-xml')
        explanationofbenefits = etree.Element('explanationofbenefits')

        data_xml.append(explanationofbenefits)
        thing.append(data_xml)
        return thing
