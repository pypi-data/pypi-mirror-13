from healthvaultlib.tests.testbase import TestBase
from healthvaultlib.methods.getvocabulary import GetVocabulary
from healthvaultlib.objects.vocabularyparameters import VocabularyParameters
from healthvaultlib.objects.vocabularykey import VocabularyKey


class TestGetVocabulary(TestBase):

    def test_getvocabulary_keys(self):
        method = GetVocabulary()
        method.execute(self.connection)

        self.assertEqual(len(method.response.vocabulary_code_set), 0)
        self.assertNotEqual(len(method.response.vocabulary_key), 0)

    def test_getvocabulary(self):
        method = GetVocabulary()

        thing = VocabularyKey()
        thing.name = 'thing-types'
        thing.family = 'wc'
        thing.version = '1'

        param = VocabularyParameters([thing])
        method.request.vocabulary_parameters = param
        method.execute(self.connection)

        self.assertNotEqual(len(method.response.vocabulary_code_set), 0)
        self.assertNotEqual(len(method.response.vocabulary_code_set[0].code_item), 0)
        self.assertEqual(len(method.response.vocabulary_key), 0)
