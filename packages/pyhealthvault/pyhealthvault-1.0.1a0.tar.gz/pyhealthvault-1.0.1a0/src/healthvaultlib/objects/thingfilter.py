from lxml import etree


class ThingFilter():

    def __init__(self):
        self.typeids = []

    def write_xml(self):
        _filter = etree.Element('filter')
        if self.typeids:
            self.add_typeids(_filter)
        return _filter

    def add_typeids(self, _filter):
        for i in self.typeids:
            typeid = etree.Element('type-id')
            typeid.text = i
            _filter.append(typeid)
