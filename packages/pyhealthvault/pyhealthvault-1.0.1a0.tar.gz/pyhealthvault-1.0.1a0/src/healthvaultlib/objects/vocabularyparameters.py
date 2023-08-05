from lxml import etree


class VocabularyParameters():

    def __init__(self, keys):
        self.vocabulary_keys = keys
        self.fixed_culture = False

    def write_xml(self):
        params = etree.Element('vocabulary-parameters')
        for i in self.vocabulary_keys:
            params.append(i.write_xml())
        fixed_culture = etree.Element('fixed-culture')
        fixed_culture.text = 'false'
        if self.fixed_culture:
            fixed_culture.text = 'true'
        params.append(fixed_culture)
        return params
