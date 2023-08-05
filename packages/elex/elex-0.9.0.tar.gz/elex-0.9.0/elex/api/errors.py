from xml.dom.minidom import parseString

class APError(Exception):
    def __init__(self, response, *args):
        self.response = response
        self.message = 'Failed with {0}'.format(response.status_code)
        messagedom = parseString(response.content)
        self.ap_message = messagedom.getElementsByTagName('Message')[0].childNodes[0].data
        import ipdb; ipdb.set_trace();
        super(APError, self).__init__(response, *args)
