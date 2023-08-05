from healthvaultlib.helpers.requestmanager import RequestManager

class Method:
    
    def __init__(self, request, response):
        self.request = request
        self.response = response

    def execute(self, connection):
        requestmgr = RequestManager(self, connection)
        requestmgr.makerequest()
