from lxml import etree

from healthvaultlib.utils.xmlutils import XmlUtils
from healthvaultlib.itemtypes.healthrecorditem import HealthRecordItem


class MedicalProblem(HealthRecordItem):

    def __init__(self, thing_xml=None):
        super(MedicalProblem, self).__init__()
        self.type_id = '5e2c027e-3417-4cfc-bd10-5a6f2e91ad23'
        if thing_xml is not None:
            self.thing_xml = thing_xml
            self.parse_thing()

    def __str__(self):
        return 'MedicalProblem'

    def parse_thing(self):
        super(MedicalProblem, self).parse_thing()
        xmlutils = XmlUtils(self.thing_xml)

    def write_xml(self):
        thing = super(MedicalProblem, self).write_xml()
        data_xml = etree.Element('data-xml')
        medicalproblem = etree.Element('medicalproblem')

        data_xml.append(medicalproblem)
        thing.append(data_xml)
        return thing
