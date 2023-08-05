from healthvaultlib.utils.xmlutils import XmlUtils
from healthvaultlib.objects.authrule import AuthRule
from healthvaultlib.objects.statement import Statement
from healthvaultlib.objects.application_binary_content import ApplicationBinaryContent


class ApplicationInfo():

    def __init__(self, info_element=None):
        self.id = None
        self.name = {}
        self.app_auth_required = None
        self.restrict_app_users = None
        self.is_published = None
        self.action_url = None
        self.description = {}
        self.auth_reason = {}
        self.domain_name = None
        self.client_service_token = None
        self.large_logo = None
        self.small_logo = {}
        self.persistent_tokens = None
        self.online_base_auth_rules = []
        self.offline_base_auth_rules = []
        self.privacy_statement = None
        self.terms_of_use = None
        self.dtc_success_message = None
        self.app_attributes = None
        self.app_type = None
        self.master_app_id = None
        self.master_app_name = None
        self.created_date = None
        self.updated_date = None
        self.valid_ip_prefixes = None
        self.vocabulary_authorizations = None
        self.child_vocabulary_authorizations_ceiling = None
        self.methods = None
        self.supported_record_locations = None
        self.supported_instances = None
        self.meaningful_use_sources = None
        self.meaningful_use_sources_ceiling = None

        if info_element is not None:
            self.parse_xml(info_element)

    def parse_xml(self, info_element):
        xmlutils = XmlUtils(info_element)

        self.id = xmlutils.get_string_by_xpath('application/id/text()')

        self.name = self.get_culture_specific_dictionary(info_element, 'name')

        self.app_auth_required = xmlutils.get_bool_by_xpath('application/app-auth-required/text()')
        self.restrict_app_users = xmlutils.get_bool_by_xpath('application/restrict-app-users/text()')
        self.is_published = xmlutils.get_bool_by_xpath('application/is-published/text()')
        self.action_url = xmlutils.get_string_by_xpath('application/action-url/text()')

        self.description = self.get_culture_specific_dictionary(info_element, 'description')
        self.auth_reason = self.get_culture_specific_dictionary(info_element, 'auth-reason')

        large_logo = info_element.xpath('application/large-logo')
        if large_logo != []:
            self.large_logo = ApplicationBinaryContent(large_logo[0])

        small_logo = info_element.xpath('application/small-logo')
        if small_logo != []:
            self.small_logo = ApplicationBinaryContent(small_logo[0])

        online_rules = info_element.xpath('application/person-online-base-auth-xml/auth/rules/rule')
        if online_rules != []:
            for rule in online_rules:
                self.online_base_auth_rules.append(AuthRule(rule))
        offline_rules = info_element.xpath('application/person-offline-base-auth-xml/auth/rules/rule')
        if offline_rules != []:
            for rule in offline_rules:
                self.offline_base_auth_rules.append(AuthRule(rule))
        if info_element.xpath('application/privacy-statement') != []:
            self.privacy_statement = Statement(info_element.xpath('application/privacy-statement')[0])
        if info_element.xpath('application/terms-of-use') != []:
            self.terms_of_use = Statement(info_element.xpath('application/terms-of-use')[0])
        if info_element.xpath('application/dtc-success-message') != []:
            self.dtc_success_message = Statement(info_element.xpath('application/dtc-success-message')[0])
    
    def get_culture_specific_dictionary(self, info_element, key):
        XMLNS = '{http://www.w3.org/XML/1998/namespace}'
        result = {}
        for entry in info_element.xpath('application/' + key):
            lang = entry.get(XMLNS + 'lang', default='')
            result[lang] = entry.xpath('text()')[0]
        return result
