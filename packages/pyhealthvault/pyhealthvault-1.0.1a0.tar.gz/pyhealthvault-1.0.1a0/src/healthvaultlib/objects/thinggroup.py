from lxml import etree
from healthvaultlib.exceptions.healthserviceexception import HealthServiceException


class ThingGroup():
    '''
        ThingGroup acts as a filter for the GetThings request.

        Attributes:
            filters              Specifies a filter for things to be retrieved
                                  based on the properties of the thing.
            format               Specifies a view for the results.
            current_version_only Specifies whether or not we should return
                                  only the current version of things that
                                  satisfy the filter.
            intents              Specifies the usage intentions for items
                                  retrieved in the group.
            order_by             Specifies the order in which to return the
                                  things being retrieved.
            ids                  Specifies thing ids that need to be returned.
            keys                 Specifies keys of things to be fetched.
            client_thing_ids     Specifies client assigned ids of things
                                  to be fetched.
            name                 Name of this request group.
            max                  The maximum number of items to be returned
                                  for this group.
            max_full             Maximum number of "full" items to be
                                  returned for this group.
    '''

    def __init__(self):
        self.filters = []
        self.format = None
        self.current_version_only = True
        self.intents = None
        self.order_by = None
        self.ids = []
        self.keys = []
        self.client_thing_ids = []

        self.name = None
        self.max = None
        self.max_full = None

    def write_xml(self):
        group = etree.Element('group')

        # Only one of the follwing three properties must go in a request,
        # hence the check.
        if self.ids:
            for i in self.ids:
                id_node = etree.Element('id')
                id_node.text = i
                group.append(id_node)
        elif self.keys:
            for i in self.keys:
                key_node = etree.Element('key')
                key_node.append(i.write_xml())
                group.append(key_node)
        elif self.client_thing_ids:
            for i in self.client_thing_ids:
                client_thing_id = etree.Element('client-thing-id')
                client_thing_id.text = i
                group.append(client_thing_id)

        for i in self.filters:
            group.append(i.write_xml())

        if self.format is not None:
            group.append(self.format.write_xml())
        else:
            raise HealthServiceException('Specify a format')

        if not self.current_version_only:
            current = etree.Element('current-version-only')
            current.text = 'false'
            group.append(current)

        if self.intents is not None:
            group.append(self.intents.write_xml())

        if self.order_by is not None:
            order_by = etree.Element('order-by')
            order_by.append(self.order_by.write_xml())
            group.append(order_by)

        if self.name is not None:
            group.attrib['name'] = self.name
        if self.max is not None:
            group.attrib['max'] = str(self.max)
        if self.max_full is not None:
            group.attrib['max-full'] = str(self.max_full)
        return group
