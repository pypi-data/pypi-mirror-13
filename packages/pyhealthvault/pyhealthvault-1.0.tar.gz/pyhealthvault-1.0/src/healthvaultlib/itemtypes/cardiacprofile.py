from lxml import etree

from healthvaultlib.utils.xmlutils import XmlUtils
from healthvaultlib.itemtypes.healthrecorditem import HealthRecordItem


class CardiacProfile(HealthRecordItem):

    def __init__(self, thing_xml=None):
        super(CardiacProfile, self).__init__()
        self.type_id = 'adaf49ad-8e10-49f8-9783-174819e97051'
        if thing_xml is not None:
            self.thing_xml = thing_xml
            self.parse_thing()

    def __str__(self):
        return 'CardiacProfile'

    def parse_thing(self):
        super(CardiacProfile, self).parse_thing()
        xmlutils = XmlUtils(self.thing_xml)

    def write_xml(self):
        thing = super(CardiacProfile, self).write_xml()
        data_xml = etree.Element('data-xml')
        cardiacprofile = etree.Element('cardiacprofile')

        data_xml.append(cardiacprofile)
        thing.append(data_xml)
        return thing
