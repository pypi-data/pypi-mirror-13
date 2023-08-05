from healthvaultlib.utils.xmlutils import XmlUtils


class UpdatedRecord:
    '''
        Attributes:
            record_id   Record id
            update_date Date in which the record was last updated
    '''

    def __init__(self, xml=None):
        self.record_id = None
        self.update_date = None

        if xml is not None:
            self.parse_xml(xml)

    def parse_xml(self, xml):
        xmlutils = XmlUtils(xml)
        self.record_id = xmlutils.get_string_by_xpath('record-id')
        self.update_date = xmlutils.get_datetime('update-date')
