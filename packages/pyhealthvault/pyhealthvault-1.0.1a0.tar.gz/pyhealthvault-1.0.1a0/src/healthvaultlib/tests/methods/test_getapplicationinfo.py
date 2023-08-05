from healthvaultlib.tests.testbase import TestBase
from healthvaultlib.methods.getapplicationinfo import GetApplicationInfo

class TestGetApplicationInfo(TestBase):
    
    def test_getapplicationinfo(self):
        method = GetApplicationInfo(True)
        method.execute(self.connection)

        response = method.response

        self.assertIsNotNone(response)
