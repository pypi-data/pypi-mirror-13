from healthvaultlib.tests.testbase import TestBase
from healthvaultlib.methods.getauthorizedrecords import GetAuthorizedRecords


class TestGetAuthorizedRecords(TestBase):

    def test_getauthroizedrecords(self):
        method = GetAuthorizedRecords([self.connection.recordid,
                                       self.connection.personid])
        method.execute(self.connection)

        response = method.response

        self.assertEqual(len(response.records), 1)
        self.assertIsNotNone(response.records[0].id)
        self.assertEqual(response.records[0].id, self.connection.recordid)
