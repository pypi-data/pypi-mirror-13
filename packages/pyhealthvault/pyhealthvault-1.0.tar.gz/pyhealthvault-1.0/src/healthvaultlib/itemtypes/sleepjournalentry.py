from lxml import etree

from healthvaultlib.utils.xmlutils import XmlUtils
from healthvaultlib.itemtypes.healthrecorditem import HealthRecordItem


class SleepJournalEntry(HealthRecordItem):

    def __init__(self, thing_xml=None):
        super(SleepJournalEntry, self).__init__()
        self.type_id = '031f5706-7f1a-11db-ad56-7bd355d89593'
        if thing_xml is not None:
            self.thing_xml = thing_xml
            self.parse_thing()

    def __str__(self):
        return 'SleepJournalEntry'

    def parse_thing(self):
        super(SleepJournalEntry, self).parse_thing()
        xmlutils = XmlUtils(self.thing_xml)

    def write_xml(self):
        thing = super(SleepJournalEntry, self).write_xml()
        data_xml = etree.Element('data-xml')
        sleepjournalentry = etree.Element('sleepjournalentry')

        data_xml.append(sleepjournalentry)
        thing.append(data_xml)
        return thing
