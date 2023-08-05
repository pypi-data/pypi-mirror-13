from lxml import etree


class ThingGroup():

    def __init__(self, filters):
        self._format = None
        self.filters = filters

    def write_xml(self):
        group = etree.Element('group')
        for i in self.filters:
            group.append(i.write_xml())
        if self._format is not None:
            group.append(self._format.write_xml())
        return group
