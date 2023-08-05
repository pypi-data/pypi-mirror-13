from lxml import etree

from healthvaultlib.utils.xmlutils import XmlUtils
from healthvaultlib.itemtypes.healthrecorditem import HealthRecordItem


class EducationSifStudentAcademicRecord(HealthRecordItem):

    def __init__(self, thing_xml=None):
        super(EducationSifStudentAcademicRecord, self).__init__()
        self.type_id = 'c3353437-7a5e-46be-8e1a-f93dac872a68'
        if thing_xml is not None:
            self.thing_xml = thing_xml
            self.parse_thing()

    def __str__(self):
        return 'EducationSifStudentAcademicRecord'

    def parse_thing(self):
        super(EducationSifStudentAcademicRecord, self).parse_thing()
        xmlutils = XmlUtils(self.thing_xml)

    def write_xml(self):
        thing = super(EducationSifStudentAcademicRecord, self).write_xml()
        data_xml = etree.Element('data-xml')
        educationsifstudentacademicrecord = etree.Element('educationsifstudentacademicrecord')

        data_xml.append(educationsifstudentacademicrecord)
        thing.append(data_xml)
        return thing
