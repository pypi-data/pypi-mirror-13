import pytz
from lxml import etree
from datetime import datetime, date

from healthvaultlib.utils.xmlutils import XmlUtils
from healthvaultlib.objects.thingkey import ThingKey

class HealthRecordItem(object):
    
    def __init__(self):
        self.thing_xml = None
        
        self.key = None

        self.type_id = None
        self.type_name = None

        self.thing_state = 'Active'
        self.flags = 0

        self.effective_date = None

        self.source = None

    def parse_thing(self):
        xmlutils = XmlUtils(self.thing_xml)
        self.key = ThingKey(self.thing_xml.xpath('thing-id')[0])

        self.type_id = xmlutils.get_string_by_xpath('type-id/text()')
        self.type_name = xmlutils.get_string_by_xpath('type-id/@name')

        self.thing_state = xmlutils.get_string_by_xpath('thing-state/text()')
        self.flags = xmlutils.get_int_by_xpath('flags/text()')
        self.effective_date = xmlutils.get_datetime_by_xpath('eff-date/text()')

        self.source = xmlutils.get_string_by_xpath('data-xml/common/source/text()')

    def write_xml(self):
        thing = etree.Element('thing')

        if self.key is not None:
            thing_id = etree.Element('thing-id')
            thing_id.text = self.key.thing_id
            thing_id.set('version-stamp', self.key.version_stamp)
            thing.append(thing_id)

        type_id = etree.Element('type-id')
        type_id.text = self.type_id
        if self.type_name is not None:
            type_id.set('name', self.type_name)
        thing.append(type_id)

        thing_state = etree.Element('thing-state')
        thing_state.text = self.thing_state
        thing.append(thing_state)

        flags = etree.Element('flags')
        flags.text = str(self.flags)
        thing.append(flags)
        
        if self.effective_date is not None:
            effective_date = etree.Element('eff-date')
            effective_date.text = self.effective_date.isoformat()
            thing.append(effective_date)

        return thing

    def get_when_node(self, node_name, whendate=None):
        if whendate is None:
            whendate = datetime.now(pytz.utc)
        when = etree.Element(node_name)

        date = etree.Element('date')
        
        y = etree.Element('y')
        y.text = str(whendate.year)
        date.append(y)

        m = etree.Element('m')
        m.text = str(whendate.month)
        date.append(m)

        d = etree.Element('d')
        d.text = str(whendate.day)
        date.append(d)

        when.append(date)

        if isinstance(whendate, datetime):
            time = etree.Element('time')

            h = etree.Element('h')
            h.text = str(whendate.hour)
            time.append(h)

            minutes = etree.Element('m')
            minutes.text = str(whendate.minute)
            time.append(minutes)

            s = etree.Element('s')
            s.text = str(whendate.second)
            time.append(s)

            when.append(time)
        return when

