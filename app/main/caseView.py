# -*- coding: utf-8 -*-
from flask import render_template,request,jsonify,session
from .framework.main import send_request,CheckError,case_template,parseScript
from .framework.methods import *
from ..models import db,Api,ApiCase
from flask.ext.login import login_required
from jinja2 import Template
from . import url

caseitem_template = """
{% for case,api in case_api %}
<tr id="caseitem_{{ case.id }}">
    <td id="casename_{{ case.id }}"><a href='javascript:;' onclick="editcase({{ case.id }})" title="{{case.desc}}">{{ case.name }}</a></td>
    <td id="relateapi_{{ case.id }}">{{ api.name }}</td>
    <td>
        <a href="javascript:;" onclick="delcase({{ case.id }})"><span class="glyphicon glyphicon-remove"></span></a>
    </td>
</tr>
{% endfor %}
"""

@url.route("/cases")
@login_required
def cases():
    session["result"] = {
        "ok":None,
        "messages":[],
        "successChecks":[],
        "failedChecks":[]
    }
    apis = Api.query.all()
    cases = ApiCase.query.all()
    return render_template("cases.html",apis=apis,cases=cases)

@url.route("/sendcaserequest",methods=["POST"])
@login_required
def sendcaserequest():
    import time

    session["result"] = {
        "messages":[],
        "successChecks":[],
        "failedChecks":[]
    }
    info = {"result":True,"errorMsg":None,"ok":None,"success":0,"failed":0,"messages":None}
    apiid = int(request.form.get("apiid"))
    api = Api.query.filter_by(id=apiid).first()
    name = request.form.get("name")
    desc = request.form.get("desc")
    script = request.form.get("script").strip()
    purpose = request.form.get("purpose")

    if purpose == "run":
        actionParser = parseScript(script)

        case = Template(case_template).render(
            beforeAction = actionParser.beforeAction,
            afterAction = actionParser.actions,
            printActions = actionParser.printActions,
            api = api,
            checkActions = actionParser.checkActions,
            purpose = purpose
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
    elif purpose == "save":
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
    elif purpose == "edit":
        print("edit case",name)
        try:
            caseid = int(request.form.get("caseid"))
            case = ApiCase.query.filter_by(id=caseid).first()
            if case:
                case.name = name.strip()
                case.desc = desc.strip()
                case.content = script.strip()
                db.session.add(case)
                db.session.commit()
            else:
                info = {"result":False,"errorMsg":"该用例不存在或已被删除"}
        except Exception as e:
            info["result"] = False
            info["errorMsg"] = "数据库异常"
    else:
        info = {"result":False,"errorMsg":"不支持的请求！"}

    return jsonify(info)

@url.route("/freshcasetable")
@login_required
def freshcasetable():
    from jinja2 import Template
    case_api = [(case,Api.query.filter_by(id=case.apiid).first()) for case in ApiCase.query.all()]
    casetable = Template(caseitem_template).render(
        case_api = case_api
    )
    return casetable

@url.route("/delcase/<int:id>",methods=["POST"])
@login_required
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
@login_required
def getcaseinfo(id):
    info = {"result":True,"api_id":None,"name":None,"desc":None,"content":None}
    try:
        case = ApiCase.query.filter_by(id=id).first()
        if case:
            info["api_id"] = case.apiid
            info["content"] = case.content
            info["name"] = case.name
            info["desc"] = case.desc
        else:
            info = {"result":False,"errorMsg":"该用例不存在或已被删除"}
    except Exception as e:
        info = {"result":False,"errorMsg":str(e)}

    return jsonify(info)
