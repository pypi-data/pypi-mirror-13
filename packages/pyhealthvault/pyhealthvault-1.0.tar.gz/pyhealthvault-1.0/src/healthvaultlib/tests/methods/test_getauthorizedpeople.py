import pytz
from datetime import datetime

from healthvaultlib.tests.testbase import TestBase
from healthvaultlib.methods.getauthorizedpeople import GetAuthorizedPeople
from healthvaultlib.objects.getauthorizedpeopleparameters import GetAuthorizedPeopleParameters


class TestGetAuthorizedPeople(TestBase):

    def test_getauthroizedpeople(self):
        method = GetAuthorizedPeople(GetAuthorizedPeopleParameters())
        method.execute(self.connection)

        response = method.response

        self.assertNotEqual(len(response.authorized_people), 0)
        self.assertIsNotNone(response.authorized_people[0].name)
        self.assertNotEqual(len(response.authorized_people[0].records), 0)

    def test_getauthroizedpeople_with_since(self):
        params = GetAuthorizedPeopleParameters()
        params.authorizations_created_since = datetime.now(pytz.utc)
        method = GetAuthorizedPeople(params)
        method.execute(self.connection)

        response = method.response

        self.assertIsNotNone(response)
        self.assertEqual(len(response.authorized_people), 0)

    def test_getauthroizedpeople_with_num(self):
        params = GetAuthorizedPeopleParameters()
        params.num_results = 1
        method = GetAuthorizedPeople(params)
        method.execute(self.connection)

        response = method.response

        self.assertIsNotNone(response)
        self.assertEqual(len(response.authorized_people), 1)
