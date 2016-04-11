# -*- coding: utf-8 -*-
from collections import OrderedDict,namedtuple
from . import web_apidoc
import json,requests

support_methodlist = [
    ("设置headers","headers = {}"),
    ("设置超时时间","timeout = (2,5)"),
    ("发送请求","send_request('login',data=data)"),
    ("设置headers1", "headers = {}"),
    ("设置超时时间2", "timeout = (2,5)"),
    ("发送请求3", "send_request('login',data=data)"),
    ("设置headers4", "headers = {}"),
    ("设置超时时间5", "timeout = (2,5)"),
    ("发送请求6", "send_request('login',data=data)")
]

support_methods = OrderedDict()

for item in support_methodlist:
    support_methods[item[0]] = item[1]

class EmptyObj(object):
    def __init__(self):
        pass

class ResponseObj(object):
    def __init__(self,apiname,url,resp):
        self._currentnode = self
        self.name = apiname
        self.url = url
        self.success = resp.ok
        self.headers = resp.headers
        self.cookies = resp.cookies
        self.elapsed = round(resp.elapsed.microseconds/1000000,2)
        self.returncode = resp.status_code
        if resp.ok:
            self.errorMsg = None
            try:
                self.data = resp.json()
                self.__initialize(resp.json())
            except Exception as e:
                self.data = resp.text
        else:
            self.data = None
            self.errorMsg = "%s %s" % (resp.status_code, resp.reason)

    def __initialize(self,obj):
        newobj = OrderedDict()
        orders,single,multi = [],[],[]
        for key,value in obj.items():
            if isinstance(value,dict):
                multi.append((key,json.dumps(value)))
            else:
                single.append((key,value))

        orders = single + multi

        for item in orders:
            newobj[item[0]] = item[1]

        for key,value in newobj.items():
            try:
                value = eval(value)
            except:
                pass
            if isinstance(value,dict):
                setattr(self._currentnode,key,EmptyObj())
                self._currentnode = eval("self._currentnode.%s" % key)
                for k in value.keys():
                    setattr(self._currentnode,k,EmptyObj())
                self.__initialize(value)
            else:
                setattr(self._currentnode,key,value)

class APIS(object):
    def __init__(self,name,apilist):
        self.name = name
        self.apis= [api['name'] for api in apilist]
        self.__initialize(apilist)

    def __initialize(self,apilist):
        for a in apilist:
            if hasattr(self,a["name"]):
                print("[warning]api:%s is already exists,ignored" %a["name"])
                continue
            setattr(self,a["name"],api(url=a["url"],type=a["type"],request=a["request"],response=a["response"]))

    def __repr__(self):
        return "<%s>" %self.name

api = namedtuple("api", "url type request response")
apilist = [eval("web_apidoc.%s" %api) for api in dir(web_apidoc) if not api.startswith("_")]
apis = APIS("SuimeAPI",apilist)

def send_request(api_name,url=None,method=None,data=None,headers=None,timeout=None):
    resp = None

    if not url and not method:
        api = eval("apis.%s" %api_name)
        url = api.url
        method = api.type

    if method == "post":
        resp = requests.post(url,data=data,headers=headers,timeout=timeout)
    elif method == "get":
        resp = requests.get(url,data=data,headers=headers,timeout=timeout)
    else:
        print("unsupport method:",method)
        exit(-1)

    return ResponseObj(api_name,url,resp)