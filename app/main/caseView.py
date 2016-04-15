# -*- coding: utf-8 -*-
from flask import render_template,request,jsonify,session
from .framework.main import support_methods,send_request,CheckError
from ..models import db,Api,ApiCase
from jinja2 import Template
from . import url
import json

case_template = """
headers = {}
data = {}
timeout = (10,15)
{% for si in setItems %}
{{ si }}{% endfor %}

response = send_request('{{api.name}}',url='{{api.url}}',method='{{api.type}}',data=data,headers=headers,timeout=timeout)

{% if purpose == 'run' %}
session["result"]["messages"].append("-"*30+"以下为请求信息"+"-"*30)
session["result"]["messages"].append("[请求]{{api.name}}:{{api.url}} {{api.type}}")
session["result"]["messages"].append("[返回码]:%s" %response.returncode)
session["result"]["messages"].append("[返回内容]:")
session["result"]["messages"].append("    "+str(response.data))
session["result"]["messages"].append("-"*28+"以下为[print]信息"+"-"*28)
{% else %}{% endif %}

{% for ac in actions %}{{ ac }}{% endfor %}

{% if purpose == 'run' %}session["result"]["messages"].append("-"*28+"以下为[check]信息"+"-"*28){% else %}{% endif %}

{% for ci in checkItems %}if not {{ ci }}:
    session["result"]["failedChecks"].append("[failed] {{ ci }}")
else:
    session["result"]["successChecks"].append("[success]{{ ci }}")
{% endfor %}
"""

caseitem_template = """
{% for case,api in case_api %}
<tr id="caseitem_{{ case.id }}">
    <td id="id_{{ case.id }}">{{ case.id }}</td>
    <td id="casename_{{ case.id }}"><a href='javascript:;' onclick="editcase({{ case.id }})" data-toggle="modal" data-target="#gridSystemModal">{{ case.name }}</a></td>
    <td id="casedesc_{{ case.id }}">{{ case.desc }}</td>
    <td id="relateapi_{{ case.id }}">{{ api.name }}</td>
    <td>
        <button onclick="delcase({{ case.id }})">删除</button>
    </td>
</tr>
{% endfor %}
"""

@url.route("/cases")
def cases():
    session["result"] = {
        "ok":None,
        "messages":[],
        "successChecks":[],
        "failedChecks":[]
    }
    apis = Api.query.all()
    cases = ApiCase.query.all()
    return render_template("cases.html",apis=apis,cases=cases,support_methods=support_methods)

@url.route("/sendcaserequest",methods=["POST"])
def sendcaserequest():
    session["result"] = {
        "messages":[],
        "successChecks":[],
        "failedChecks":[]
    }
    info = {"result":True,"errorMsg":None,"ok":None,"success":0,"failed":0,"messages":None}
    id = int(request.form.get("id"))
    api = Api.query.filter_by(id=id).first()
    script = request.form.get("script").strip()
    purpose = request.form.get("purpose")

    if purpose == "run":
        setItems, actions, checkItems = [], [], []
        scripts = [s for s in script.split("\n") if s.strip()]

        for script in scripts:
            if script.strip().startswith("[set]"):
                setItems.append(script[5:].strip())
            elif script.strip().startswith("[check]"):
                checkItems.append(script.strip()[7:].replace("\"", "'").strip())
            elif script.strip().startswith("[print]"):
                if "response" in script:
                    actions.append("session['result']['messages'].append(str(" + script.strip()[7:].strip() + "))\r\n")
                elif script.strip()[7:].strip():
                    actions.append("session['result']['messages'].append('" + script.strip()[7:].strip() + "')\r\n")
            else:
                actions.append(script)
        case = Template(case_template).render(
            setItems=setItems,
            actions=actions,
            api=api,
            checkItems=checkItems,
            purpose=purpose
        )
        try:
            exec(case)
        except Exception as e:
            info["result"] = False
            info["errorMsg"] = str(e)

        info["messages"] = "\n".join([str(m) for m in session["result"]["messages"]]+session["result"]["failedChecks"]+session["result"]["successChecks"])
        info["success"] = len(session["result"]["successChecks"])
        info["failed"] = len(session["result"]["failedChecks"])
        info["ok"] = False if session["result"]["failedChecks"] else True
    else:
        name = request.form.get("name")
        desc = request.form.get("desc")
        case = ApiCase.query.filter_by(name=name).first()
        if case:
            info["result"] = False
            info["errorMsg"] = "该名称的用例已存在"
        else:
            try:
                case = ApiCase(name,desc,script)
                db.session.add(case)
                db.session.commit()
                api.apicases.append(case)
                db.session.add(api)
                db.session.commit()
            except Exception as e:
                info["result"] = False
                info["errorMsg"] = "数据库异常"

    return jsonify(info)

@url.route("/freshcasetable")
def freshcasetable():
    from jinja2 import Template
    case_api = [(case,Api.query.filter_by(id=case.api_id).first()) for case in ApiCase.query.all()]
    casetable = Template(caseitem_template).render(
        case_api = case_api
    )
    return casetable

@url.route("/delcase/<int:id>",methods=["POST"])
def delcase(id):
    info = {"result":True,"errorMsg":None}
    case = ApiCase.query.filter_by(id=id).first()
    if case:
        try:
            db.session.delete(case)
            db.session.commit()
        except Exception as e:
            info = {"result":False,"errorMsg":str(e)}
    else:
        info = {"result":False,"errorMsg":"该用例不存在或已被删除"}

    return jsonify(info)

@url.route("/getcaseinfo/<int:id>")
def getcaseinfo(id):
    info = {"result":True,"name":None,"desc":None,"content":None}
    try:
        case = ApiCase.query.filter_by(id=id).first()
        if case:
            info["content"] = case.content
            info["name"] = case.name
            info["desc"] = case.desc
        else:
            info = {"result":False,"errorMsg":"该用例不存在或已被删除"}
    except Exception as e:
        info = {"result":False,"errorMsg":str(e)}

    return jsonify(info)
