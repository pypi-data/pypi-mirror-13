from lxml import etree

from healthvaultlib.utils.xmlutils import XmlUtils
from healthvaultlib.itemtypes.healthrecorditem import HealthRecordItem


class Weight(HealthRecordItem):

    def __init__(self, thing_xml=None):
        super(Weight, self).__init__()
        self.type_id = '3d34d87e-7fc1-4153-800f-f56592cb0d17'
        self.when = None
        self.value_kg = None
        self.display_value = None
        self.display_units = None
        if thing_xml is not None:
            self.thing_xml = thing_xml
            self.parse_thing()

    def __str__(self):
        return 'Weight'

    def parse_thing(self):
        super(Weight, self).parse_thing()
        if self.thing_xml.xpath('data-xml') != []:
            xmlutils = XmlUtils(self.thing_xml)
            when_node = self.thing_xml.xpath('data-xml/weight/when')
            if len(when_node) > 0:
                self.when = xmlutils.get_datetime_from_when(when_node[0])
            self.value_kg = xmlutils.get_float_by_xpath('data-xml/weight/value/kg/text()')
            self.display_value = xmlutils.get_float_by_xpath('data-xml/weight/value/display/text()')
            self.display_unit = xmlutils.get_string_by_xpath('data-xml/weight/value/display/@units')
        else:
            self.is_partial = True

    def write_xml(self):
        thing = super(Weight, self).write_xml()
        data_xml = etree.Element('data-xml')
        weight = etree.Element('weight')

        weight.append(self.get_when_node('when', self.when))

        value = etree.Element('value')
        kg = etree.Element('kg')
        kg.text = str(self.value_kg)
        value.append(kg)

        if self.display_value is not None and self.display_units is not None:
            display = etree.Element('display')
            display.text = str(self.display_value)
            display.set('units', self.display_units)
            value.append(display)
        weight.append(value)

        data_xml.append(weight)
        thing.append(data_xml)
        return thing
