from lxml import etree
from healthvaultlib.exceptions.healthserviceexception import HealthServiceException


class VocabularySearchParams:

    allowed_modes = ['Prefix', 'Contains', 'FullText']

    def __init__(self, search_string):
        self.search_string = search_string
        self.max_results = None
        self.search_mode = None

    def write_xml(self):
        params = etree.Element('text-search-parameters')

        search_string = etree.Element('search-string')
        search_string.text = self.search_string
        if self.search_mode is not None:
            if self.search_mode not in self.allowed_modes:
                raise HealthServiceException('Invalid Xml')
            search_string.attrib['search-mode'] = self.search_mode
        params.append(search_string)

        if self.max_results is not None:
            max_results = etree.Element('max-results')
            max_results.text = str(self.max_results)
            params.append(max_results)
        return params
