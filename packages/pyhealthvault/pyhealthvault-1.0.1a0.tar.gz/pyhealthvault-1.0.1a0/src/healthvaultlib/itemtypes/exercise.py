from lxml import etree

from healthvaultlib.utils.xmlutils import XmlUtils
from healthvaultlib.itemtypes.healthrecorditem import HealthRecordItem


class Exercise(HealthRecordItem):

    def __init__(self, thing_xml=None):
        super(Exercise, self).__init__()
        self.type_id = '85a21ddb-db20-4c65-8d30-33c899ccf612'
        if thing_xml is not None:
            self.thing_xml = thing_xml
            self.parse_thing()

    def __str__(self):
        return 'Exercise'

    def parse_thing(self):
        super(Exercise, self).parse_thing()
        xmlutils = XmlUtils(self.thing_xml)

    def write_xml(self):
        thing = super(Exercise, self).write_xml()
        data_xml = etree.Element('data-xml')
        exercise = etree.Element('exercise')

        data_xml.append(exercise)
        thing.append(data_xml)
        return thing
