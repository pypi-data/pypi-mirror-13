import pytz
import hmac
import base64
import socket
import hashlib
import httplib
import datetime
import urlparse

from lxml import etree

from healthvaultlib.exceptions.healthserviceexception import HealthServiceException


class RequestManager():

    def __init__(self, method, connection):
        self.info = None
        self.header = None
        self.auth = None
        self.method = method
        self.connection = connection

    def construct_request(self):
        self.info = self.method.request.get_info()
        infohash = base64.encodestring(hashlib.sha1(etree.tostring(self.info)).digest()).strip()
        self.header = self.construct_header(infohash)
        if self.connection.shared_secret is not None:
            hashedheader = hmac.new(base64.b64decode(self.connection.shared_secret),
                                    etree.tostring(self.header), hashlib.sha1)
            hashedheader64 = base64.encodestring(hashedheader.digest()).strip()
            self.auth = self.construct_auth(hashedheader64)

    def construct_auth(self, hashedheader):
        auth = etree.Element('auth')

        hmac_data = etree.Element('hmac-data', algName='HMACSHA1')
        hmac_data.text = hashedheader
        auth.append(hmac_data)

        return auth

    def makerequest(self):
        self.construct_request()
        NSMAP = {'wc-request': 'urn:com.microsoft.wc.request'}
        root_name = etree.QName('urn:com.microsoft.wc.request', 'request')
        request_wrapper = etree.Element(root_name, nsmap=NSMAP)
        if self.auth is not None:
            request_wrapper.append(self.auth)
        request_wrapper.append(self.header)
        request_wrapper.append(self.info)

        retry_count = 0
        MAX_RETRY = 3
        while retry_count < MAX_RETRY:
            retry_count += 1
            print 'Trial number %d' % (retry_count)
            print '[REQUEST]'
            print etree.tostring(request_wrapper)

            response = self.sendrequest(etree.tostring(request_wrapper))

            print '[RESPONSE]'
            print etree.tostring(response, pretty_print=True)
            try:
                action = self.manage_exception(response)
                if action == 0:
                    # All OK, continue to parse response
                    # and break retry loop
                    self.method.response.parse_response(response)
                    break
            except HealthServiceException as e:
                if retry_count == MAX_RETRY:
                    raise e
                else:
                    continue

    def manage_exception(self, response):
        status_code = int(response.xpath('/response/status/code/text()')[0])
        if status_code == 0:
            # All successful, method worked as expected
            return 0
        if status_code == 8:
            # Auth token expired, return a NZ int,
            # this will cause the SDK to retry request
            self.connection.connect()
            return 1
        if status_code != 0:
            error_description = response.xpath('/response/status/error/message/text()')[0]
            raise HealthServiceException(error_description)

    def sendrequest(self, request):
        '''
            Recieves a request xml as a string and posts it
            to the health service url specified in the
            settings.py
        '''
        url = urlparse.urlparse(self.connection.healthserviceurl)
        conn = None
        if url.scheme == 'https':
            conn = httplib.HTTPSConnection(url.netloc)
        else:
            conn = httplib.HTTPConnection(url.netloc)
        conn.putrequest('POST', url.path)
        conn.putheader('Content-Type', 'text/xml')
        conn.putheader('Content-Length', '%d' % len(request))
        conn.endheaders()
        try:
            conn.send(request)
        except socket.error, v:
            if v[0] == 32:      # Broken pipe
                conn.close()
            raise
        response = conn.getresponse().read()
        return etree.fromstring(response)

    def construct_header(self, infohash):
        header = etree.Element('header')

        method = etree.Element('method')
        method.text = self.method.request.name
        header.append(method)

        method_version = etree.Element('method-version')
        method_version.text = str(self.method.request.version)
        header.append(method_version)

        if self.connection.targetpersonid is not None:
            target_person_id = etree.Element('target-person-id')
            target_person_id.text = self.connection.targetpersonid
            header.append(target_person_id)

        if self.connection.recordid is not None:
            record_id = etree.Element('record-id')
            record_id.text = self.connection.recordid
            header.append(record_id)

        if self.connection.auth_token is not None:
            auth_session = etree.Element('auth-session')

            auth_token = etree.Element('auth-token')
            auth_token.text = self.connection.auth_token
            auth_session.append(auth_token)

            if self.connection.user_auth_token is not None:
                user_auth_token = etree.Element('user-auth-token')
                user_auth_token.text = self.connection.user_auth_token
                auth_session.append(user_auth_token)
            else:
                offline_person_info = etree.Element('offline-person-info')
                offline_person_id = etree.Element('offline-person-id')
                offline_person_id.text = self.connection.personid
                offline_person_info.append(offline_person_id)
                auth_session.append(offline_person_info)

            header.append(auth_session)
        else:
            appid = etree.Element('app-id')
            appid.text = self.connection.applicationid
            header.append(appid)

        language = etree.Element('language')
        language.text = 'en'
        header.append(language)

        country = etree.Element('country')
        country.text = 'US'
        header.append(country)

        msg_time = etree.Element('msg-time')
        msg_time.text = datetime.datetime.now(pytz.utc).isoformat()
        header.append(msg_time)

        msg_ttl = etree.Element('msg-ttl')
        msg_ttl.text = '3600'
        header.append(msg_ttl)

        version = etree.Element('version')
        version.text = '1.0'
        header.append(version)

        info_hash = etree.Element('info-hash')
        hash_data = etree.Element('hash-data', algName='SHA1')
        hash_data.text = infohash
        info_hash.append(hash_data)
        header.append(info_hash)

        return header
