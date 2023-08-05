from lxml import etree

from healthvaultlib.utils.xmlutils import XmlUtils
from healthvaultlib.itemtypes.healthrecorditem import HealthRecordItem


class PersonalPicture(HealthRecordItem):

    def __init__(self, thing_xml=None):
        super(PersonalPicture, self).__init__()
        self.type_id = 'a5294488-f865-4ce3-92fa-187cd3b58930'
        if thing_xml is not None:
            self.thing_xml = thing_xml
            self.parse_thing()

    def __str__(self):
        return 'PersonalPicture'

    def parse_thing(self):
        super(PersonalPicture, self).parse_thing()
        xmlutils = XmlUtils(self.thing_xml)

    def write_xml(self):
        thing = super(PersonalPicture, self).write_xml()
        data_xml = etree.Element('data-xml')
        personalpicture = etree.Element('personalpicture')

        data_xml.append(personalpicture)
        thing.append(data_xml)
        return thing
