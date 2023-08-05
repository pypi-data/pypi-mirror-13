import pytz
import datetime

from lxml import etree

from healthvaultlib.hvcrypto import HVCrypto
from healthvaultlib.methods.method import Method
from healthvaultlib.utils.xmlutils import XmlUtils
from healthvaultlib.methods.methodbase import RequestBase, ResponseBase

class CreateAuthenticatedSessionTokenRequest(RequestBase):

    def __init__(self, connection):
        super(CreateAuthenticatedSessionTokenRequest, self).__init__()
        self.name = 'CreateAuthenticatedSessionToken'
        self.version = 2
        self.connection = connection

    def get_info(self):
        content = self.construct_content()
        info = self.construct_info(content)
        return info

    def construct_content(self):
        content = etree.Element('content')

        appid = etree.Element('app-id')
        appid.text = self.connection.applicationid
        content.append(appid)

        _hmac = etree.Element('hmac')
        _hmac.text = 'HMACSHA1'
        content.append(_hmac)

        signing_time = etree.Element('signing-time')
        signing_time.text = datetime.datetime.now(pytz.utc).isoformat()
        content.append(signing_time)

        return content

    def construct_info(self, content):
        info = etree.Element('info')
        auth_info = etree.Element('auth-info')
        app_id = etree.Element('app-id')
        app_id.text = self.connection.applicationid
        auth_info.append(app_id)
        info.append(auth_info)

        crypto = HVCrypto(self.connection.publickey, self.connection.privatekey)

        credential = etree.Element('credential')
        appserver2 = etree.Element('appserver2')
        sig = etree.Element('sig', digestMethod='SHA1', sigMethod='RSA-SHA1', thumbprint=self.connection.thumbprint)
        sig.text = crypto.sign(etree.tostring(content))
        appserver2.append(sig)

        appserver2.append(content)
        credential.append(appserver2)
        auth_info.append(credential)
        info.append(auth_info)

        return info

class CreateAuthenticatedSessionTokenResponse(ResponseBase):
    
    def __init__(self):
        super(CreateAuthenticatedSessionTokenResponse, self).__init__()
        self.shared_secret = None
        self.auth_token = None
        self.name = 'CreateAuthenticatedSessionToken'
        self.version = 2

    def parse_response(self, response):
        self.parse_info(response)
        xmlutils = XmlUtils(self.info)
        self.shared_secret = xmlutils.get_string_by_xpath('shared-secret/text()')
        self.auth_token = xmlutils.get_string_by_xpath('token/text()')

class CreateAuthenticatedSessionToken(Method):
    
    def __init__(self, connection):
        self.request = CreateAuthenticatedSessionTokenRequest(connection)
        self.response = CreateAuthenticatedSessionTokenResponse()
