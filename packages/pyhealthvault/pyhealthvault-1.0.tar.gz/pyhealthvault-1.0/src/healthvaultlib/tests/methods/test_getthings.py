from healthvaultlib.tests.testbase import TestBase
from healthvaultlib.methods.getthings import GetThings
from healthvaultlib.objects.thinggroup import ThingGroup
from healthvaultlib.objects.thingfilter import ThingFilter
from healthvaultlib.objects.thingformat import ThingFormat

class TestGetThings(TestBase):
    
    def test_getthings(self):
        height_filter = ThingFilter()
        height_format = ThingFormat()
        height_format.sections.append('core')
        height_format.sections.append('xml')
        height_filter.typeids.append('40750a6a-89b2-455c-bd8d-b420a4cb500b')
        group = ThingGroup([height_filter])
        group._format = height_format

        method = GetThings([group])
        method.execute(self.connection)

        self.assertEqual(len(method.response.groups), 1)

        if method.response.groups[0].healthrecorditems:
            item = method.response.groups[0].healthrecorditems[0]
            self.assertEqual('40750a6a-89b2-455c-bd8d-b420a4cb500b', item.type_id)
            self.assertIsNotNone(item.value_m)

    def test_getthings_coreonly(self):
        height_filter = ThingFilter()
        height_format = ThingFormat()
        height_format.sections.append('core')
        height_filter.typeids.append('40750a6a-89b2-455c-bd8d-b420a4cb500b')
        group = ThingGroup([height_filter])
        group._format = height_format

        method = GetThings([group])
        method.execute(self.connection)

        self.assertEqual(len(method.response.groups), 1)

        if method.response.groups[0].healthrecorditems:
            item = method.response.groups[0].healthrecorditems[0]
            self.assertEqual('40750a6a-89b2-455c-bd8d-b420a4cb500b', item.type_id)
            self.assertIsNone(item.value_m)
