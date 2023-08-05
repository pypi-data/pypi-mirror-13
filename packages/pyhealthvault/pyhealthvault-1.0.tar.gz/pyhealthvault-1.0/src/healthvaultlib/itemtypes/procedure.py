from lxml import etree

from healthvaultlib.utils.xmlutils import XmlUtils
from healthvaultlib.itemtypes.healthrecorditem import HealthRecordItem


class Procedure(HealthRecordItem):

    def __init__(self, thing_xml=None):
        super(Procedure, self).__init__()
        self.type_id = 'df4db479-a1ba-42a2-8714-2b083b88150f'
        if thing_xml is not None:
            self.thing_xml = thing_xml
            self.parse_thing()

    def __str__(self):
        return 'Procedure'

    def parse_thing(self):
        super(Procedure, self).parse_thing()
        xmlutils = XmlUtils(self.thing_xml)

    def write_xml(self):
        thing = super(Procedure, self).write_xml()
        data_xml = etree.Element('data-xml')
        procedure = etree.Element('procedure')

        data_xml.append(procedure)
        thing.append(data_xml)
        return thing
