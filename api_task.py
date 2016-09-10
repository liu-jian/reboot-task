import os,re,imp,json

data1 = {'id':2,'jsonrpc':'2.0','method':'idc.get','auth':None,'params':{'a':'ok'}}
d1 = json.dumps(data1,sort_keys=True,indent=4)
decodejson = json.loads(d1)

class Autoload(object):
    def __init__(self, module_name):
        self.moduledir = "/home/www/test"
        self.module = None
        self.module_name = module_name
        self.method = None

    def isValidMethod(self, func=None):
        self.method = func
#        print self.method,self.module
        return hasattr(self.module, self.method)

    def isValidModule(self):
        return self._load_module()

    def getCallmethod(self):
        if hasattr(self.module, self.method):
            return self.method
        else:
            return None


    def _load_module(self):
        ret = False
        for filename in os.listdir(self.moduledir):
            if re.search(r".+\.(py)$", filename):
                module_name = filename.replace('.py','')
                if module_name == self.module_name:
                    fp, pathname, desc = imp.find_module(module_name, [self.moduledir])
                    if not fp:
                        continue
                    try:
                        self.module = imp.load_module(module_name, fp, pathname, desc)
                        ret = True
                    except:
                        fp.close()
                    break
        return ret

class Response(object):
    def __init__(self):
        self.data = None
        self.errorCode = 0
        self.errorMassage = None

class JsonRpc(object):
    def __init__(self, data_in):
        self.data_in = json.loads(data_in)
        self.response = None


    def excute(self):
        if self.data_in.get('id', False) is False:
            self.data_in.setdefault('id', 1)
        val = self.validata()
        if val:
            x = self.data_in['method']
            module = x.split('.')[0]
            method = x.split('.')[1]
            auth = self.data_in['auth']
	    params = self.data_in['params']
#	    self.response = self.callMethod(module, method, params, auth)
            self.callMethod(module, method, params, auth)
#            print 'JsonRpc.excute'
#            print self.response['jsonrpc']
        else:
            print self.response
            return self.response 

    def callMethod(self, module, func, params, auth):
        response = Response()
	at = Autoload(module)
        if not at.isValidModule():
	    response.errorCode = -200
	    response.errorMassage = 'can not load module:%s' % module
	    return response
	elif not at.isValidMethod(func):
	    response.errorCode = -201
	    response.errorMassage = 'can not find %s' % func
	    return response
	else:
	    flag = self.requiresAuthentication(module, func)
	    if (flag is False) and (auth is not None):
                print 'flag'
	        response.errorCode = -202
		response.errorMassage = 'something wrong!'
		return response
            elif flag:
	        if auth is not None:
		    response.errorCode = -203
		    response.errorMassage = 'no token!'
		    return response
                else:
		    called = at.getCallmethod()
		    if at.isValidMethod(called):
                        print called
                        method = getattr(at.module,called)
                        print method()
		        response.data = method()
			self.processResult(response)
		    else:
		        response.errorCode = -204
			response.errorMassage = 'cat not run method'
			return response
                print 'before'
                print response.errorMassage
                print '#########'
		return response

    def jsonError(self, id, errno, data=None):
        VERSION = self.data_in['jsonrpc']
        _error = True
        format_error = {
            "jsonrpc": VERSION,
            "error": data,
            "id": id,
            "errno": errno
        }
	self.response = format_error

    def processResult(self, response):
        VERSION = self.data_in['jsonrpc']
        if response.errorCode != 0:
	    errno = response.errorCode
	    id = self.data_in['id']
	    error = "error"
	    self.jsonError(id, errno,error)
	else:
	    formatResp = {
	        "jsonrpc": VERSION,
		"result": response.data,
		"id": self.data_in['id']
	    }
	    self.response = formatResp

    def requiresAuthentication(self, module, func):
        if module == "user" and func == "login":
	    return False
	else:
	    return True


    def validata(self):
        if self.data_in['jsonrpc'] != '2.0':
            id = self.data_in['id']
            error = 'jsonrpc\'s version is wrong!'
            errno = -100
            self.jsonError(id,errno,error)
            return False
        if self.data_in.get('method', False) is False:
            id = self.data_in['id']
            error = 'can\'t get method!'
            errno = -101
            self.jsonError(id,errno,error)
            return False
        if self.data_in.get('params', False) is False:
            id = self.data_in['id']
            error = 'can\'t get params!'
            errno = -102
            self.jsonError(id,errno,error)
            return False
        return True


x = JsonRpc(d1)
x.excute()
print x.response['result']
