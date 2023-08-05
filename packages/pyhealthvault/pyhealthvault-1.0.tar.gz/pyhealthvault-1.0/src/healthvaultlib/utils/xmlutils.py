from dateutil import parser
from datetime import datetime
from lxml import etree

class XmlUtils:

    def __init__(self, element=None):
        self.element = element

    def get_string_by_xpath(self, xpath):
        if self.element is None:
            return None
        result = self.element.xpath(xpath)
        if len(result) > 0:
            out = result[0]
            if isinstance(out, str):
                return out
            if hasattr(out, 'text'):
                return out.text
        return None

    def get_int_by_xpath(self, xpath):
        value = self.get_string_by_xpath(xpath)
        return int(value) if value is not None else None

    def get_bool_by_xpath(self, xpath):
        value = self.get_string_by_xpath(xpath)
        return value == 1 if value is not None else False

    def get_float_by_xpath(self, xpath):
        value = self.get_string_by_xpath(xpath)
        return float(value) if value is not None else None

    def get_datetime_by_xpath(self, xpath):
        value = self.get_string_by_xpath(xpath)
        return parser.parse(value) if value is not None else None

    def get_datetime_from_when(self, when_node):
        xmlutils = XmlUtils(when_node)
        y = xmlutils.get_int_by_xpath('date/y/text()')
        m = xmlutils.get_int_by_xpath('date/m/text()')
        d = xmlutils.get_int_by_xpath('date/d/text()')
        h = xmlutils.get_int_by_xpath('time/h/text()')
        _m = xmlutils.get_int_by_xpath('time/m/text()')
        s = xmlutils.get_int_by_xpath('time/s/text()')
        if h is None:
            return datetime(y, m, d)
        else:
            return datetime(y, m, d, h, _m, s)

    def get_string(self, attributename):
        value = self.element.get(attributename)
        return value if value is not None else None

    def get_bool(self, attributename):
        value = self.get_string(attributename)
        return value == 1

    def get_int(self, attributename):
        value = self.get_string(attributename)
        return int(value) if value is not None else None

    def get_float(self, attributename):
        value = self.get_string(attributename)
        return float(value) if value is not None else None

    def get_datetime(self, attributename):
        value = self.get_string(attributename)
        return parser.parse(value) if value is not None else None

    def get_lang(self):
        XMLNS = '{http://www.w3.org/XML/1998/namespace}'
        lang = XMLNS + 'lang'
        return self.get_string(lang)
