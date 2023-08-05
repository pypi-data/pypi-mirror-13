class Permission:

    flags = {}

    def __init__(self, permission_xml=None):
        self.permission = 0
        self.init_permission_flags()

        if permission_xml is not None:
            self.parse_xml(permission_xml)

    def parse_xml(self, permission_xml):
        for i in permission_xml.xpath('permission'):
            self.add_permission(i.xpath('./text()')[0])

    def init_permission_flags(self):
        if self.flags:
            return
        self.flags['Read'] = 1
        self.flags['Update'] = 2
        self.flags['Create'] = 4
        self.flags['Delete'] = 8

    def add_permission(self, permission):
        self.permission |= self.flags[permission]

    def __str__(self):
        return str(self.permission)
