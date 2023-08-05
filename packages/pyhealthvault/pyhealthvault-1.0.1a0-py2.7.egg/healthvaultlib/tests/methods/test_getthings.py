from healthvaultlib.tests.testbase import TestBase
from healthvaultlib.methods.getthings import GetThings
from healthvaultlib.objects.thinggroup import ThingGroup
from healthvaultlib.objects.thingfilter import ThingFilter
from healthvaultlib.objects.thingformat import ThingFormat
from healthvaultlib.objects.thingorderbyspecs import ThingOrderBySpecs
from healthvaultlib.objects.thingintentsspec import ThingIntentsSpec
from healthvaultlib.exceptions.healthserviceexception import HealthServiceException


class TestGetThings(TestBase):

    def test_getthings(self):
        typeid = '40750a6a-89b2-455c-bd8d-b420a4cb500b'
        height_filter = ThingFilter()
        height_format = ThingFormat()
        height_format.sections.append('core')
        height_format.sections.append('xml')
        height_filter.typeids.append(typeid)
        group = ThingGroup()
        group.filters = [height_filter]
        group.format = height_format

        method = GetThings([group])
        method.execute(self.connection)

        self.assertEqual(len(method.response.groups), 1)

        if method.response.groups[0].healthrecorditems:
            item = method.response.groups[0].healthrecorditems[0]
            self.assertEqual(typeid, item.type_id)
            self.assertIsNotNone(item.value_m)

    def test_getthings_coreonly(self):
        typeid = '40750a6a-89b2-455c-bd8d-b420a4cb500b'
        height_filter = ThingFilter()
        height_format = ThingFormat()
        height_format.sections.append('core')
        height_filter.typeids.append(typeid)
        group = ThingGroup()
        group.filters = [height_filter]
        group.format = height_format

        method = GetThings([group])
        method.execute(self.connection)

        self.assertEqual(len(method.response.groups), 1)

        if method.response.groups[0].healthrecorditems:
            item = method.response.groups[0].healthrecorditems[0]
            self.assertEqual(typeid, item.type_id)
            self.assertIsNone(item.value_m)

    def test_getthings_order_by(self):
        # Height does not support sorting, hence weight
        typeid = '3d34d87e-7fc1-4153-800f-f56592cb0d17'
        weight_filter = ThingFilter()
        weight_format = ThingFormat()
        weight_format.sections.append('core')
        weight_format.sections.append('xml')
        weight_filter.typeids.append(typeid)

        order_by = ThingOrderBySpecs(typeid, 'When')
        order_by.direction = 'Desc'

        group = ThingGroup()
        group.filters = [weight_filter]
        group.format = weight_format
        group.order_by = order_by

        method = GetThings([group])
        method.execute(self.connection)

        self.assertEqual(len(method.response.groups), 1)

        if method.response.groups[0].healthrecorditems:
            items = method.response.groups[0].healthrecorditems
            self.assertEqual(typeid, items[0].type_id)
            self.assertIsNotNone(items[0].value_kg)
            self.assertTrue(items[0].when > items[1].when)

    def test_getthings_max(self):
        typeid = '40750a6a-89b2-455c-bd8d-b420a4cb500b'
        height_filter = ThingFilter()
        height_format = ThingFormat()
        height_format.sections.append('core')
        height_format.sections.append('xml')
        height_filter.typeids.append(typeid)

        group = ThingGroup()
        group.filters = [height_filter]
        group.format = height_format
        group.max = 5
        group.max_full = 3

        method = GetThings([group])
        method.execute(self.connection)

        self.assertEqual(len(method.response.groups), 1)

        if method.response.groups[0].healthrecorditems:
            items = method.response.groups[0].healthrecorditems
            self.assertEqual(typeid, items[0].type_id)
            self.assertTrue(len(items) <= 5)

            if len(items) > 3:
                self.assertIsNotNone(items[2].value_m)
                self.assertIsNone(items[3].value_m)
                self.assertTrue(items[3].is_partial)

    def test_getthings_validations_and_intents(self):
        typeid = '40750a6a-89b2-455c-bd8d-b420a4cb500b'
        height_filter = ThingFilter()
        height_format = ThingFormat()
        height_format.sections.append('core')
        height_format.sections.append('xml')
        height_filter.typeids.append(typeid)

        group = ThingGroup()
        group.filters = [height_filter]

        method = GetThings([group])
        with self.assertRaises(HealthServiceException):
            method.execute(self.connection)

        group.format = height_format
        group.intents = ThingIntentsSpec(['view', 'pingu'])

        method = GetThings([group])
        with self.assertRaises(HealthServiceException):
            method.execute(self.connection)

        group.intents = ThingIntentsSpec(['view', 'download'])
        method = GetThings([group])
        method.execute(self.connection)

        self.assertEqual(len(method.response.groups), 1)

        if method.response.groups[0].healthrecorditems:
            items = method.response.groups[0].healthrecorditems
            self.assertEqual(typeid, items[0].type_id)
