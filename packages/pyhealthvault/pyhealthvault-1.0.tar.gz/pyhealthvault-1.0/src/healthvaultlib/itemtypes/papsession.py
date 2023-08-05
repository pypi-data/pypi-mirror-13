from lxml import etree

from healthvaultlib.utils.xmlutils import XmlUtils
from healthvaultlib.itemtypes.healthrecorditem import HealthRecordItem


class PapSession(HealthRecordItem):

    def __init__(self, thing_xml=None):
        super(PapSession, self).__init__()
        self.type_id = '9085cad9-e866-4564-8a91-7ad8685d204d'
        if thing_xml is not None:
            self.thing_xml = thing_xml
            self.parse_thing()

    def __str__(self):
        return 'PapSession'

    def parse_thing(self):
        super(PapSession, self).parse_thing()
        xmlutils = XmlUtils(self.thing_xml)

    def write_xml(self):
        thing = super(PapSession, self).write_xml()
        data_xml = etree.Element('data-xml')
        papsession = etree.Element('papsession')

        data_xml.append(papsession)
        thing.append(data_xml)
        return thing
