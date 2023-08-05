from healthvaultlib.itemtypes.itemtype_resolver import ItemTypeResolver


class ThingGroupResponse():

    def __init__(self, group_xml):
        self.healthrecorditems = []
        resolver = ItemTypeResolver()
        for healthrecorditem in group_xml.xpath('thing'):
            typeid = healthrecorditem.xpath('type-id/text()')[0]
            item = resolver.get_class(typeid)(healthrecorditem)
            self.healthrecorditems.append(item)
