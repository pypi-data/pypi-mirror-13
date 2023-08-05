from lxml import etree
from healthvaultlib.itemtypes.healthrecorditem import HealthRecordItem
from healthvaultlib.utils.xmlutils import XmlUtils


class Height(HealthRecordItem):

    def __init__(self, thing_xml=None):
        super(Height, self).__init__()
        self.type_id = '40750a6a-89b2-455c-bd8d-b420a4cb500b'
        self.when = None
        self.display_value = None
        self.display_units = None
        self.value_m = None
        if thing_xml is not None:
            self.thing_xml = thing_xml
            self.parse_thing()

    def __str__(self):
        if self.display_value is not None:
            return ("%f%s" % (self.display_value, self.display_unit))
        else:
            return ("%f%s" % (self.value_m, 'm'))

    def parse_thing(self):
        super(Height, self).parse_thing()
        xmlutils = XmlUtils(self.thing_xml)
        when_node = self.thing_xml.xpath('data-xml/height/when')
        if len(when_node) > 0:
            self.when = xmlutils.get_datetime_from_when(when_node[0])
        self.value_m = xmlutils.get_float_by_xpath('data-xml/height/value/m/text()')
        self.display_value =  xmlutils.get_float_by_xpath('data-xml/height/value/display/text()')
        self.display_unit =  xmlutils.get_string_by_xpath('data-xml/height/value/display/@units')

    def write_xml(self):
        thing = super(Height, self).write_xml()
        data_xml = etree.Element('data-xml')
        height = etree.Element('height')

        height.append(self.get_when_node('when', self.when))

        value = etree.Element('value')
        m = etree.Element('m')
        m.text = str(self.value_m)
        value.append(m)

        if self.display_value is not None and self.display_units is not None:
            display = etree.Element('display')
            display.text = str(self.display_value)
            display.set('units', self.display_units)
            value.append(display)
        height.append(value)
        data_xml.append(height)
        thing.append(data_xml)
        return thing
