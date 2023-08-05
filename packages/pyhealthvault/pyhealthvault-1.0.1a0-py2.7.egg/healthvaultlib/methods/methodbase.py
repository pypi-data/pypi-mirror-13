from lxml import etree

class MethodBase(object):
    
    def __init__(self, name, version):
        self.name = name
        self.version = version

class RequestBase(MethodBase):
    
    def __init__(self):
        pass


class ResponseBase(MethodBase):

    def __init__(self):
        self.info = None
        self.NSMAP = None

    def set_info_namespace(self):
        if self.version  == 1:
            return {'wc' : ('urn:com.microsoft.wc.methods.response.%s' % (self.name))}
        return {'wc' : ('urn:com.microsoft.wc.methods.response.%s%d' % (self.name, self.version))}

    def parse_info(self, response):
        if self.NSMAP is None:
            self.NSMAP = self.set_info_namespace()
        self.info = response.xpath('/response/wc:info', namespaces=self.NSMAP)[0]
