class ApplicationBinaryContent:
    
    def __init__(self, content_xml=None):
        self.content_type = ''
        self.culture_specific_content = {}

        if content_xml is not None:
            self.parse_xml(content_xml)

    def parse_xml(self, content_xml):
        XMLNS = '{http://www.w3.org/XML/1998/namespace}'
        for content in content_xml.xpath('logo'):
            self.culture_specific_content[content.get(XMLNS + 'lang', default='')] = content.xpath('text()')[0]
        self.content_type = content_xml.xpath('content-type/text()')[0]
