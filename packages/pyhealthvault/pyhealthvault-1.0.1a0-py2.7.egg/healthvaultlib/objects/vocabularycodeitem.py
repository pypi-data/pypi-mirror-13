from healthvaultlib.utils.xmlutils import XmlUtils


class VocabularyCodeItem:
    '''
        Describes an indivdual code item.

        Attributes:
            code_value          This is the value associated with the item 
                                which uniquelyidentifies it within a 
                                vocabulary.
            display_text        This is the display text of the item.
            abbreviation_text   This is the abbreviation text of an item.
            info_xml            Contains important auxillary information that can be used
                                for operations such as unit conversions.
    '''

    def __init__(self, xml=None):
        '''
            :param xml: lxml.etree.Element representing a single VocabularyItem
        '''
        self.code_value = None
        self.display_text = None
        self.abbreviation_text = None
        self.info_xml = None

        if xml is not None:
            self.parse_xml(xml)

    def parse_xml(self, xml):
        '''
            :param xml: lxml.etree.Element representing a single VocabularyItem
        '''
        xmlutils = XmlUtils(xml)
        self.code_value = xmlutils.get_string_by_xpath('code-value')
        self.display_text = xmlutils.get_string_by_xpath('display-text')
        self.abbreviation_text = xmlutils.get_string_by_xpath('abbreviation-text')
        info_xml = xml.xpath('info-xml')
        if info_xml != []:
            self.info_xml = info_xml[0]
