from lxml import etree

from healthvaultlib.utils.xmlutils import XmlUtils
from healthvaultlib.itemtypes.healthrecorditem import HealthRecordItem


class ExerciseSamples(HealthRecordItem):

    def __init__(self, thing_xml=None):
        super(ExerciseSamples, self).__init__()
        self.type_id = 'e1f92d7f-9699-4483-8223-8442874ec6d9'
        if thing_xml is not None:
            self.thing_xml = thing_xml
            self.parse_thing()

    def __str__(self):
        return 'ExerciseSamples'

    def parse_thing(self):
        super(ExerciseSamples, self).parse_thing()
        xmlutils = XmlUtils(self.thing_xml)

    def write_xml(self):
        thing = super(ExerciseSamples, self).write_xml()
        data_xml = etree.Element('data-xml')
        exercisesamples = etree.Element('exercisesamples')

        data_xml.append(exercisesamples)
        thing.append(data_xml)
        return thing
