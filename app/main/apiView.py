# -*- coding: utf-8 -*-
from flask import render_template,request,jsonify
from . import url
from ..models import db,Api
from .framework.main import apilist,send_request,support_methods
import json

@url.route("/apis")
def showapi():
    apis = Api.query.all()
    return render_template("apis.html",apis=apis)

def stringToJson(data):
    try:
        data = eval(data)
    except Exception as e:
        if "{" not in data and "}" not in data and "=" in data:
            args = [line for line in data.split("\n") if line.strip()]
            data = {}
            for arg in args:
                k,v  = arg.split("=")
                try:
                    data[k.strip()] = eval(v.strip())
                except:
                    data[k.strip()] = v.strip()
        else:
            data = {}
    return data

@url.route("/testapi",methods=["POST"])
def testapi():
    info = {"result":True,"response":None,"errorMsg":None}
    method = request.form.get("method").lower()
    url = request.form.get("url")
    data = request.form.get("data")
    headers = request.form.get("headers")
    data = stringToJson(data)
    headers = stringToJson(headers)

    try:
        res = send_request("testapi",url=url,method=method,data=data,headers=headers)
        resp = {
            "statusCode":res.returncode,
            "elapsed":res.elapsed,
            "success":res.success,
            "errorMsg":res.errorMsg,
            "data":json.dumps(res.data,indent=4,ensure_ascii=False),
            "headers":dict(res.headers),
            "cookies":dict(res.cookies)
        }

        info["response"] = resp
    except Exception as e:
        info = {"result":False,"errorMsg":str(e)}

    return jsonify(info)

api_template = """
{% for api in apis %}
<tr id="apiitem_{{ api.id }}">
    <td id="apitype_{{ api.id }}">{{ api.type }}</td>
    <td id="apiname_{{ api.id }}"><a href='javascript:;' onclick="editcase({{ api.id }},'{{ api.type }}','{{ api.name }}','{{ api.url }}')" data-toggle="modal" data-target="#gridSystemModal">{{ api.name }}</a></td>
    <td id="apiurl_{{ api.id }}">{{ api.url }}</td>
    <td>
        <button onclick="delapi({{ api.id }})">删除</button>
    </td>
</tr>
{% endfor %}
"""

@url.route("/freshapitable")
def freshapitable():
    from jinja2 import Template
    apis = Api.query.all()
    apitable = Template(api_template).render(
        apis = apis
    )
    return apitable

@url.route("/saveapi",methods=["POST"])
def saveapi():
    info = {"result":True,"errorMsg":None}
    name = request.form.get("name").strip()
    url = request.form.get("url").strip()
    method = request.form.get("method")
    args = {}
    if "?" in url:
        url,argstr = url.split('?')
        for arg in argstr.split("&"):
            k,v = arg.split("=")
            args[k] = v

    reqdata = request.form.get("reqdata").strip()
    respdata = request.form.get("respdata").strip()
    reqheader = request.form.get("reqheader").strip()
    respheader = request.form.get("respheader").strip()
    reqdata = stringToJson(reqdata)
    respdata = stringToJson(respdata)
    reqheader = stringToJson(reqheader)
    respheader = stringToJson(respheader)

    try:
        api = Api(name,url,method,headers=reqheader,reqdata=reqdata if reqdata else args,respdata=respdata)
        db.session.add(api)
        db.session.commit()
    except Exception as e:
        info = {"result":False,"errorMsg":str(e)}
    finally:
        #print(name,url,method,reqdata,respdata,reqheader,respheader)
        return jsonify(info)

@url.route("/editapi/<int:id>",methods=["POST"])
def editapi(id):
    info = {"result":True,"errorMsg":None}
    api = Api.query.filter_by(id=id).first()
    if api:
        name = request.form.get("name").strip()
        type = request.form.get("type")
        url = request.form.get("url").strip()
        api.name = name
        api.type = type
        api.url = url
        db.session.add(api)
        db.session.commit()
    else:
        info = {"result":False,"errorMsg":"该接口不存在或已被删除"}

    return jsonify(info)

@url.route("/delapi/<int:id>",methods=["POST"])
def delapi(id):
    info = {"result":True,"errorMsg":None}
    api = Api.query.filter_by(id=id).first()
    if api:
        try:
            db.session.delete(api)
            db.session.commit()
        except Exception as e:
            info = {"result":False,"errorMsg":str(e)}
    else:
        info = {"result":False,"errorMsg":"该接口不存在或已被删除"}

    return jsonify(info)

# data = {
#     "cellphone":18516042356,
#     "password":"6547436690a26a399603a7096e876a2d"
# }
#
# headers = {
#     "token":""
# }
#
# res_login = request('login',data=data)
#
# if res_login.success:
#     headers["token"] = res_login.body.token
#
# res_stinfo = request("order_all",data={"pageSize":10,"page":1,"token":res_login.body.token},headers=headers)
#
# print(res_stinfo.url,res_stinfo.returncode)
# pprint(res_stinfo.data)



# login = api.login
# stinfo = api.getstudentinfo
# res_stinfo = None
# res_login = None
# print("[action]start request login:",login.url)
# if login.type == "get":
#     res_login = send_get('login', login.url, data=data)
# elif login.type == "post":
#     res_login = send_post('login',login.url,data=data)
# else:
#     exit(-1)
#
# if res_login.success:
#     token = res_login.body.token
#     print("[success] token:",token,res_login.elapsed)
#     print("[action] start request getstudentinfo:",stinfo.url)
#     if stinfo.type == "get":
#         res_stinfo = send_get('getinfo',stinfo.url,headers={"token":token})
#     elif stinfo.type == "post":
#         res_stinfo = send_post('getinfo', stinfo.url, headers={"token": token})
#     else:
#         exit(-1)
#     if res_stinfo.success:
#         print("[success] elapsed:",res_stinfo.elapsed)
#         pprint(res_stinfo.data)
#     else:
#         print("[failed] elapsed:", res_stinfo.elapsed)
#         print(res_stinfo.errorMsg)
# else:
#     print("[failed] elapsed:", res_login.elapsed)
#     print(res_login.errorMsg)