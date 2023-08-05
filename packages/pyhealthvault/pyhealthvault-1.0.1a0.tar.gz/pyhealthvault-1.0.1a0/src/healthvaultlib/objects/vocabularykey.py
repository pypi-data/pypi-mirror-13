from lxml import etree
from healthvaultlib.utils.xmlutils import XmlUtils


class VocabularyKey:
    '''
        VocabularyKey is a key to a set of vocabularies.

        Atrributes:
            name            Vocabulary name. This attribute is mandatory when
                            is used in GetVocabulary method.
            family          Vocabulary family
            version         Vocabulary version
            code_value      Vocabulary coded value
            description     Vocabulary decription
            language        Vocabulary language
    '''

    def __init__(self, key_xml=None):
        '''
            :param key_xml: lxml.etree.Element representing a single VocabularyKey
        '''
        self.name = None
        self.family = None
        self.version = None
        self.code_value = None
        self.description = None

        self.language = None

        if key_xml is not None:
            self.parse_xml(key_xml)

    def write_xml(self):
        '''
            Writes a VocabularyKey Xml as per Healthvault schema.

            :returns: lxml.etree.Element representing a single VocabularyKey
        '''
        key = None
        if self. language is not None:
            lang = {}
            lang['{http://www.w3.org/XML/1998/namespace}lang'] = self.language
            key = etree.Element('vocabulary-key', attrib=lang)
        else:
            key = etree.Element('vocabulary-key')

        name = etree.Element('name')
        name.text = self.name
        key.append(name)

        if self.family is not None:
            family = etree.Element('family')
            family.text = self.family
            key.append(family)

        if self.version is not None:
            version = etree.Element('version')
            version.text = self.version
            key.append(version)

        if self.code_value is not None:
            code_value = etree.Element('code-value')
            code_value.text = self.code_value
            key.append(code_value)

        return key

    def parse_xml(self, key_xml):
        '''
            Parse a VocabularyKey from an Xml as per Healthvault
            schema.

            :param key_xml: lxml.etree.Element representing a single VocabularyKey
        '''
        xmlutils = XmlUtils(key_xml)
        self.name = xmlutils.get_string_by_xpath('name')
        self.family = xmlutils.get_string_by_xpath('family')
        self.version = xmlutils.get_string_by_xpath('version')
        self.description = xmlutils.get_string_by_xpath('description')

        self.language = xmlutils.get_lang()
