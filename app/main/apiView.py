# -*- coding: utf-8 -*-
from .framework.main import send_request
from .framework.methods import *
from flask.ext.login import current_user,login_required
from flask import render_template,request,jsonify,abort
from jinja2 import Template
from ..models import db,Api
from . import url
import json

@url.route("/apis")
def showapi():
    apis = Api.query.filter_by(userid=current_user.id).all() if hasattr(current_user, "nickname") else []
    return render_template("apis.html",apis=apis)

def stringToJson(data):
    try:
        data = eval(data)
    except Exception as e:
        if "{" not in data and "}" not in data and "=" in data and "Error" not in data:
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
    <td id="apiname_{{ api.id }}"><a href='javascript:;' onclick="editapi({{ api.id }},'{{ api.type }}','{{ api.name }}','{{ api.url }}')" data-toggle="modal" data-target="#gridSystemModal">{{ api.name }}</a></td>
    <td id="apiurl_{{ api.id }}">{{ api.url }}</td>
    <td>
        <button onclick="delapi({{ api.id }})">删除</button>
    </td>
</tr>
{% endfor %}
"""

@url.route("/freshapitable")
def freshapitable():
    apis = Api.query.filter_by(userid=current_user.id).all() if hasattr(current_user,"nickname") else []
    apitable = Template(api_template).render(
        apis = apis
    )
    return apitable

@url.route("/saveapi",methods=["POST"])
@login_required
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
        api = Api(name,url,method,current_user.id,headers=reqheader,reqdata=reqdata if reqdata else args,respdata=respdata)
        db.session.add(api)
        db.session.commit()
    except Exception as e:
        info = {"result":False,"errorMsg":str(e)}
    finally:
        return jsonify(info)

@url.route("/editapi/<int:id>",methods=["POST"])
def editapi(id):
    info = {"result":True,"errorMsg":None}
    api = Api.query.filter_by(id=id).filter_by(userid=current_user.id).first()
    if api:
        if api.userid != current_user.id:
            abort(401)
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
    api = Api.query.filter_by(id=id).filter_by(userid=current_user.id).first()
    if api:
        if api.userid != current_user.id:
            abort(401)
        try:
            db.session.delete(api)
            db.session.commit()
        except Exception as e:
            info = {"result":False,"errorMsg":str(e)}
    else:
        info = {"result":False,"errorMsg":"该接口不存在或已被删除"}

    return jsonify(info)