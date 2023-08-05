from lxml import etree

from healthvaultlib.utils.xmlutils import XmlUtils
from healthvaultlib.itemtypes.healthrecorditem import HealthRecordItem


class MealDefinition(HealthRecordItem):

    def __init__(self, thing_xml=None):
        super(MealDefinition, self).__init__()
        self.type_id = '074e122a-335a-4a47-a63d-00a8f3e79e60'
        if thing_xml is not None:
            self.thing_xml = thing_xml
            self.parse_thing()

    def __str__(self):
        return 'MealDefinition'

    def parse_thing(self):
        super(MealDefinition, self).parse_thing()
        xmlutils = XmlUtils(self.thing_xml)

    def write_xml(self):
        thing = super(MealDefinition, self).write_xml()
        data_xml = etree.Element('data-xml')
        mealdefinition = etree.Element('mealdefinition')

        data_xml.append(mealdefinition)
        thing.append(data_xml)
        return thing
