from healthvaultlib.tests.testbase import TestBase
from healthvaultlib.methods.getservicedefinition import GetServiceDefinition

class TestGetServiceDefinition(TestBase):
    
    def test_getservicedefinition(self):
        method = GetServiceDefinition(['platform', 'shell', 'topology',
                                       'xml-over-http-methods', 'meaningful-use'])
        method.execute(self.connection)

        self.assertIsNotNone(method.response)
        self.assertIsNotNone(method.response.service_definition.platform)
        self.assertIsNotNone(method.response.service_definition.shell)
        self.assertNotEqual(len(method.response.service_definition.xml_method), 0)
        self.assertNotEqual(len(method.response.service_definition.common_schema), 0)
        self.assertNotEqual(len(method.response.service_definition.instances), 0)
        self.assertIsNotNone(method.response.service_definition.meaningful_use)
        self.assertIsNotNone(method.response.service_definition.updated_date)
