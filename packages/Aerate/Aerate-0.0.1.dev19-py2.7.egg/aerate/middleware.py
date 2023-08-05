
class OpMiddleware(object):
    '''
    '''
    def __init__(self):
        self.ops = {}

    def addOp(self, opid, op):
        self.ops[opid] = op

    def process_resource(self, req, resp, resource):
        pass
        # key = resource.__class__.__name__ + '_on_' + req.method.lower()
        # try:
        #     req.context['op'] = self.ops[key]
        # except KeyError:
        #     raise KeyError('{0} not found in operations'.format(key))
