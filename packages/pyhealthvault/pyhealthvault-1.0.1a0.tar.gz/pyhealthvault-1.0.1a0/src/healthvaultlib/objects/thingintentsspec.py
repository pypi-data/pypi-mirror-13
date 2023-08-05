from lxml import etree
from healthvaultlib.exceptions.healthserviceexception import HealthServiceException


class ThingIntentsSpec:
    '''
        Specifies the usage intentions for items retrieved in the group.

        Attributes:
            intents     The value may be one of "view", "download",
                        or "transmit".
    '''

    allowed_intents = ['view', 'download', 'transmit']

    def __init__(self, intents):
        self.intents = intents

    def write_xml(self):
        intents = etree.Element('intents')

        for i in self.intents:
            if i not in self.allowed_intents:
                raise HealthServiceException('Invalid intent')
            intent = etree.Element('intent')
            intent.text = i
            intents.append(intent)
        return intents
