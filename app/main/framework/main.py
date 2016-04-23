# -*- coding: utf-8 -*-
from collections import OrderedDict,namedtuple
import json,requests,time

case_template = \
"""
{% if suit %}
logger = Logger('%s/{{suit.name }}/{{ timenow }}/{{api.name}}_{{ case.case_name }}_{{currentCount}}' %current_user.nickname)
info = {
    "name":'{{ case.case_name }}',
    "desc":'{{ case.case_desc }}',
    "apiname":'{{ api.name }}',
    "logpath":'%s/{{ suit.name }}/{{ timenow }}/{{ api.name }}_{{ case.case_name }}_{{currentCount}}.log' %current_user.nickname,
    "status":0,
    "passCheck":[],
    "failCheck":[]
}

{% endif %}
headers = {}
data = {}
timeout = (10,15)

{{ beforeAction }}

response = send_request('{{api.name}}',url='{{api.url}}',method='{{api.type}}',data=data,headers=headers,timeout=timeout)

{% if purpose == 'run' %}
session["result"]["messages"].append("-"*30+"以下为请求信息"+"-"*30)
session["result"]["messages"].append("[请求]{{api.name}}:{{api.url}} {{api.type}}")
session["result"]["messages"].append("[返回码]:%s  响应时间:%s" %(response.returncode,response.elapsed))
session["result"]["messages"].append("[返回内容]:")
session["result"]["messages"].append("    "+str(response.data))
session["result"]["messages"].append("-"*28+"以下为[print]信息"+"-"*28)
{% elif purpose == 'runsuit' %}
logger.log("-"*30+"以下为请求信息"+"-"*30)
logger.log("[请求]{{api.name}}:{{api.url}} {{api.type}}")
logger.log("[返回码]:%s  响应时间:%s" %(response.returncode,response.elapsed))
logger.log("[返回内容]:")
logger.log("    "+str(response.data))
logger.log("-"*28+"以下为[print]信息"+"-"*28)
{% else %}
{% endif %}

{{ afterAction }}

{% for action in printActions %}
{% if purpose == 'run' %}
try:
    if isinstance({{action}},int) or isinstance({{action}},str) or isinstance({{action}},dict) or isinstance({{action}},list):
        session["result"]["messages"].append({{action}})
    else:
        session["result"]["messages"].append(str({{action}}))
except Exception as e:
    session["result"]["messages"].append(str(e))
{% elif purpose == 'runsuit' %}
try:
    logger.log({{action}})
except:
    logger.log(str({{action}}))
{% endif %}
{% endfor %}


{% if purpose == 'run' %}
session["result"]["messages"].append("-"*28+"以下为[check]信息"+"-"*28)
{% elif purpose == 'runsuit' %}
logger.log("-"*28+"以下为[check]信息"+"-"*28)
{% else %}
{% endif %}

{% for ca in checkActions %}
{% if purpose == 'run' %}
try:
    if not {{ ca }}:
        session["result"]["failedChecks"].append("[failed] {{ ca }}")
    else:
        session["result"]["successChecks"].append("[success]{{ ca }}")
except Exception as e:
    session["result"]["failedChecks"].append("[failed] %s" %str(e))
{% elif purpose == 'runsuit' %}
try:
    if not {{ ca }}:
        info["status"] = -1
        info["failCheck"].append("[failed] {{ ca }}")
        logger.log("[failed] {{ ca }}")
    else:
        info["passCheck"].append("[success] {{ ca }}")
        logger.log("[success] {{ ca }}")
except Exception as e:
    info["status"] = -1
    info["failCheck"].append("[failed] %s" %str(e))
    logger.log("[failed] %s" %str(e))
{% endif %}
{% endfor %}

{% if suit %}

suit.result["details"][{{currentCount}}].append(info)

{% endif %}
"""

def parseScript(script):
    sp1 = script.split("[check]")
    checkActions = [line.replace("\"", "'").strip() for line in sp1[1].strip().split("\n") if line.strip()]
    sp2 = sp1[0].split("[after]")
    actions, printActions = [], []
    for action in sp2[1].strip().split("\n"):
        if action.strip().startswith("print(") and action.strip().endswith(")"):
            printActions.append(action.split("print")[1].strip())
        else:
            if action.strip():
                actions.append(action)

    beforeAction = sp2[0].split("[before]")[1].strip()
    actionParser = namedtuple("actionParser","beforeAction actions printActions checkActions")
    return actionParser(beforeAction,'\n'.join(actions),printActions,checkActions)


class CheckError(Exception):
	def __init__(self,info):
		self.info = info

	def __str__(self):
		return self.info

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
        try:
            self.elapsed = round(resp.elapsed.microseconds/1000000,2)
        except:
            self.elapsed = round(resp.elapsed,2)
        self.returncode = resp.status_code

        if resp.ok:
            self.errorMsg = None
            try:
                self.data = resp.json()
                self.__initialize(resp.json())
            except Exception as e:
                self.data = resp.text
        else:
            try:
                self.data = resp.json()
                self.__initialize(resp.json())
            except Exception as e:
                self.data = resp.text
            self.errorMsg = "%s %s" % (resp.status_code, resp.reason)

    def __repr__(self):
        return "<ResponseObj:%s>" %self.name

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

def send_request(api_name,url=None,method=None,data=None,headers=None,timeout=None):
    resp = None
    fakeresp = namedtuple("fakeresp", "ok reason headers cookies status_code elapsed text")
    if not url and not method:
        api = eval("apis.%s" %api_name)
        url = api.url
        method = api.type
    if method.lower() == "post":
        start = time.time()
        try:
            resp = requests.post(url,data=data,headers=headers,timeout=timeout)
        except requests.exceptions.ChunkedEncodingError as e:
            elapsed = time.time() - start
            resp = fakeresp(ok=True,reason=str(e),headers={},cookies={},status_code=200,elapsed=elapsed,text="接口无返回")
        except Exception as e:
            elapsed = time.time() - start
            resp = fakeresp(ok=False, reason=str(e), headers={}, cookies={}, status_code=401, elapsed=elapsed, text=str(e))
    elif method.lower() == "get":
        start = time.time()
        try:
            resp = requests.get(url,params=data,headers=headers,timeout=timeout)
        except requests.exceptions.ChunkedEncodingError as e:
            elapsed = time.time() - start
            resp = fakeresp(ok=True, reason=str(e), headers={}, cookies={}, status_code=200, elapsed=elapsed, text="接口无返回")
        except Exception as e:
            elapsed = time.time() - start
            resp = fakeresp(ok=False, reason=str(e), headers={}, cookies={}, status_code=401, elapsed=elapsed, text=str(e))
    else:
        print("unsupport method:",method)
        exit(-1)

    return ResponseObj(api_name,url,resp)