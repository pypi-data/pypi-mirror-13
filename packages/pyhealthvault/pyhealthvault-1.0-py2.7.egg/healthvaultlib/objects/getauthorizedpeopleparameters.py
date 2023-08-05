from lxml import etree


class GetAuthorizedPeopleParameters:

    def __init__(self):
        self.person_id_cursor = None
        self.authorizations_created_since = None
        self.num_results = None

    def get_info(self):
        parameters = etree.Element('parameters')

        if self.person_id_cursor is not None:
            cursor = etree.Element('person-id-cursor')
            cursor.text = self.person_id_cursor
            parameters.append(cursor)
        if self.authorizations_created_since is not None:
            since = etree.Element('authorizations-created-since')
            since.text = self.authorizations_created_since.isoformat()
            parameters.append(since)
        if self.num_results is not None:
            num_results = etree.Element('num-results')
            num_results.text = str(self.num_results)
            parameters.append(num_results)
        return parameters
