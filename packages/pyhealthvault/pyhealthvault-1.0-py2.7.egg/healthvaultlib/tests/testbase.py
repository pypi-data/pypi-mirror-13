import unittest

import settings
from healthvaultlib.helpers.connection import Connection

class TestBase(unittest.TestCase):
    
    def setUp(self):
        self.connection = self.get_connection()
    
    def get_connection(self):
        conn = Connection(settings.HV_APPID, settings.HV_SERVICE_SERVER)
        conn.thumbprint = settings.APP_THUMBPRINT
        conn.publickey = settings.APP_PUBLIC_KEY
        conn.privatekey = settings.APP_PRIVATE_KEY
        conn.connect()
        conn.set_person_and_record(settings.OFFLINE_PERSON_ID, settings.OFFLINE_RECORD_ID)
        return conn
