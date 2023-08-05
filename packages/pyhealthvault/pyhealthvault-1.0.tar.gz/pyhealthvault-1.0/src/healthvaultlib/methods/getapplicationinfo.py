from lxml import etree
from healthvaultlib.methods.method import Method
from healthvaultlib.objects.applicationinfo import ApplicationInfo
from healthvaultlib.methods.methodbase import RequestBase, ResponseBase

class GetApplicationInfoRequest(RequestBase):
    
    def __init__(self, all_languages, child_appid):
        super(GetApplicationInfoRequest, self).__init__()
        self.name = 'GetApplicationInfo'
        self.version = 2
        self.all_languages = all_languages
        self.child_app_id = child_appid

    def get_info(self):
        info = etree.Element('info')
        if self.all_languages is not None:
            all_languages = etree.Element('all-languages')
            if self.all_languages:
                all_languages.text = 'true'
            else:
                all_languages.text = 'false'
            info.append(all_languages)
        if self.child_app_id is not None:
            child_app_id = etree.Element('child-app-id')
            child_app_id.text = self.child_app_id
            info.append(child_app_id)
        return info

class GetApplicationInfoResponse(ResponseBase):

    def __init__(self):
        super(GetApplicationInfoResponse, self).__init__()
        self.name = 'GetApplicationInfo'
        self.version = 1
        self.application_info = None

    def parse_response(self, response):
        self.parse_info(response)
        self.application_info = ApplicationInfo(self.info)

class GetApplicationInfo(Method):
    
    def __init__(self, all_languages=None, child_appid=None):
        self.request = GetApplicationInfoRequest(all_languages, child_appid)
        self.response = GetApplicationInfoResponse()
