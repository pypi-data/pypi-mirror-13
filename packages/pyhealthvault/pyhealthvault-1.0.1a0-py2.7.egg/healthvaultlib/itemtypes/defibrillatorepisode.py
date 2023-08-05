from lxml import etree

from healthvaultlib.utils.xmlutils import XmlUtils
from healthvaultlib.itemtypes.healthrecorditem import HealthRecordItem


class DefibrillatorEpisode(HealthRecordItem):

    def __init__(self, thing_xml=None):
        super(DefibrillatorEpisode, self).__init__()
        self.type_id = 'a3d38add-b7b2-4ccd-856b-9b14bbc4e075'
        if thing_xml is not None:
            self.thing_xml = thing_xml
            self.parse_thing()

    def __str__(self):
        return 'DefibrillatorEpisode'

    def parse_thing(self):
        super(DefibrillatorEpisode, self).parse_thing()
        xmlutils = XmlUtils(self.thing_xml)

    def write_xml(self):
        thing = super(DefibrillatorEpisode, self).write_xml()
        data_xml = etree.Element('data-xml')
        defibrillatorepisode = etree.Element('defibrillatorepisode')

        data_xml.append(defibrillatorepisode)
        thing.append(data_xml)
        return thing
