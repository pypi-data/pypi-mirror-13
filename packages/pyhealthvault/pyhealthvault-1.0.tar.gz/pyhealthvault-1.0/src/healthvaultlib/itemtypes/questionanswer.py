from lxml import etree

from healthvaultlib.utils.xmlutils import XmlUtils
from healthvaultlib.itemtypes.healthrecorditem import HealthRecordItem


class QuestionAnswer(HealthRecordItem):

    def __init__(self, thing_xml=None):
        super(QuestionAnswer, self).__init__()
        self.type_id = '55d33791-58de-4cae-8c78-819e12ba5059'
        if thing_xml is not None:
            self.thing_xml = thing_xml
            self.parse_thing()

    def __str__(self):
        return 'QuestionAnswer'

    def parse_thing(self):
        super(QuestionAnswer, self).parse_thing()
        xmlutils = XmlUtils(self.thing_xml)

    def write_xml(self):
        thing = super(QuestionAnswer, self).write_xml()
        data_xml = etree.Element('data-xml')
        questionanswer = etree.Element('questionanswer')

        data_xml.append(questionanswer)
        thing.append(data_xml)
        return thing
