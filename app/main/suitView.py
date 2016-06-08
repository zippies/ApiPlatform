# -*- coding: utf-8 -*-
from flask import render_template,request,jsonify,abort
from .framework.main import send_request,CheckError,case_template,parseScript
from .framework.logger import Logger
from ..models import db,Api,ApiCase,TestSuit
from flask_login import login_required,current_user
from .framework.methods import *
from jinja2 import Template
from config import Config
from . import url
import time,os,json

@url.route("/")
@url.route("/suits")
@login_required
def suits():
    apis = Api.query.filter_by(userid=current_user.id).all()
    return render_template("suits.html",apis=apis)

@url.route("/newsuit",methods=["POST"])
@login_required
def newsuit():
    info = {"result":True,"errorMsg":None}
    suitname = request.form.get("suitname").strip()
    suitcases = dict(request.form).get("suitapi_cases[]",[])
    orders = []
    orderedapi = []
    try:
        for caseid in suitcases:
            case = ApiCase.query.filter_by(id=caseid).first()
            if case:
                api = Api.query.filter_by(id=case.apiid).first()
                if api.userid != current_user.id:
                    abort(401)
                if api.id not in orderedapi:
                    orders.append({
                        "id":api.id,
                        "name":api.name,
                        "url":api.url,
                        "type":api.type,
                        "cases":[{"id":c.id,"name":c.name,"desc":c.desc} for c in api.apicases if str(c.id) in suitcases]
                    })
                    orderedapi.append(api.id)
                else:
                    continue
        if orders:
            suit = TestSuit()
            suit.name = suitname
            suit.orders = orders
            suit.userid = current_user.id
            db.session.add(suit)
            db.session.commit()
        else:
            info = {"result":False,"errorMsg":"api不存在或没有可执行的用例"}
    except Exception as e:
        info = {"result":False,"errorMsg":str(e)}
    return jsonify(info)

suit_template = \
"""
{% for suit in suits %}
<div id="suitlist_{{suit.id}}">
    测试集:<a href="javascript:void(0)">{{suit.name}}</a>
    <div class="well">
        <div id="apilist_{{ suit.id }}" class="list-group">
        {% for api in suit.orders %}
            <div api-suit-{{suit.id}}="{{api.id}}" class="list-group-item col-lg-12">
                <span class="badge" style="color:yellow">{{ api.cases|length }}</span>
                <span class="col-lg-3"><span class="glyphicon glyphicon-move" aria-hidden="true"></span> 接口:<a href="#suit_{{suit.id}}_api_{{api.id}}" data-toggle="collapse" aria-expanded="false" aria-controls="suit_{{suit.id}}_api_{{ api.id }}">{{ api.name }}</a></span>
                <span class="col-lg-7">&nbsp{{api.type}}&nbsp{{ api.url }}&nbsp&nbsp&nbsp</span>
                <div class="collapse col-lg-12" id="suit_{{suit.id}}_api_{{api.id}}" style="margin-top:20px;margin-left:30px;">
                    <div id="caselist_suit_{{suit.id}}_api_{{api.id}}" class="list-group">
                    {% for case in api.cases %}
                        <div api-suit-{{suit.id}}-api-{{api.id}}="{{case.id}}" class="list-group-item col-lg-12">
                            <span class="glyphicon glyphicon-move" aria-hidden="true"></span> 用例:<span>{{case.name}}&nbsp&nbsp&nbsp&nbsp描述:{{ case.desc }}
                        </div>
                    {% endfor %}
                    </div>
                </div>
            </div>
        {% endfor %}
        </div>
        <ul class="list-inline list-group">
            <li>运行次数:</li>
            <li><input id="runcount_{{suit.id}}" value="1" class="form-control"/></li>
            <li>
                <button id="runsuit_{{suit.id}}" onclick="runsuit({{suit.id}})" data-loading-text="正在运行" autocomplete="off" class="btn btn-default">运行</button>
            </li>
            <li><button onclick="delsuit({{suit.id}})" class="btn btn-default">删除</button></li>
            <div id="result_{{ suit.id }}" style="padding:5px">
            </div>
        </ul>
    </div>
</div>

{% endfor %}
"""

@url.route("/freshsuits")
@login_required
def freshsuits():
    data = {"suits":None,"orders":None}
    suits = TestSuit.query.filter_by(userid=current_user.id).all()

    s = Template(suit_template).render(
        suits = suits
    )

    data["suits"] = s
    data["orders"] = [[suit.id,suit.orders] for suit in suits]

    return jsonify(data)

@url.route("/delsuit/<int:id>",methods=["POST"])
@login_required
def delsuit(id):
    info = {"result":True,"errorMsg":None}
    try:
        suit = TestSuit.query.filter_by(id=id).first()
        if suit:
            if suit.userid != current_user.id:
                abort(401)
            db.session.delete(suit)
            db.session.commit()
        else:
            info = {"result": False, "errorMsg": "该测试集不存在或已被删除"}
    except Exception as e:
        info = {"result":False,"errorMsg":str(e)}
    finally:
        return jsonify(info)

def getitemfromorders(apiid,orders):
    for item in orders:
        if item["id"] == int(apiid):
            return item

@url.route("/updatesuitorder/<int:suitid>",methods=["POST"])
@login_required
def updatesuitorder(suitid):
    info = {"result":True,"errorMsg":None}
    neworder = []
    order = dict(request.form).get("api_order[]")
    try:
        suit = TestSuit.query.filter_by(id=suitid).first()
        if suit:
            if suit.userid != current_user.id:
                abort(401)
            for apiid in order:
                neworder.append(getitemfromorders(apiid,suit.orders))

            suit = TestSuit(id=suitid, orders=neworder)
            db.session.merge(suit)
            db.session.commit()
        else:
            info = {"result":False,"errorMsg":"该测试集不存在或已被删除"}
    except Exception as e:
        info = {"result":False,"errorMsg":str(e)}
    return jsonify(info)

@url.route("/updatecaseorder/<int:suitid>/<int:apiid>",methods=["POST"])
@login_required
def updatecaseorder(suitid,apiid):
    info = {"result":True,"errorMsg":None}
    caseorder = dict(request.form).get("case_order[]")
    suit = TestSuit.query.filter_by(id=suitid).first()
    neworder = []
    if suit:
        if suit.userid != current_user.id:
            abort(401)
        for item in suit.orders:
            if item["id"] == apiid:
                newcases = []
                for caseid in caseorder:
                    newcases.append(getitemfromorders(caseid,item["cases"]))
                item["cases"] = newcases
                neworder.append(item)
            else:
                neworder.append(item)

        suit = TestSuit(id=suitid, orders=neworder)
        db.session.merge(suit)
        db.session.commit()
    else:
        info = {"result":False,"errorMsg":"该测试集不存在或已被删除"}
    return jsonify(info)

@url.route("/runsuit/<int:id>")
@login_required
def runsuit(id):
    info = {"result":True,"info":None,"errorMsg":None}
    count = request.args.get("count")
    try:
        count = eval(count) if eval(count) < 10 else 1
    except:
        count = 1

    suit = TestSuit.query.filter_by(id=id).first()
    testcases = []
    if suit:
        if suit.userid != current_user.id:
            abort(401)
        for apiitem in suit.orders:
            api = Api.query.filter_by(id=int(apiitem["id"])).first()
            if api:
                for caseitem in apiitem["cases"]:
                    case = ApiCase.query.filter_by(id=int(caseitem["id"])).first()
                    if case:
                        testcases.append({
                            "api":api,
                            "case_name":case.name,
                            "case_desc":case.desc,
                            "case_content":case.content
                        })
            else:
                pass
    else:
        info = {"result":False,"errorMsg":"该测试集不存在或已被删除"}

    suit.status = 1
    db.session.add(suit)
    db.session.commit()

    timenow = time.strftime("%Y_%m_%d_%H_%M_%S")

    for i in range(count):
        suit.result["details"][i] = []
        for case in testcases:
            actionParser = parseScript(case["case_content"])
            c = Template(case_template).render(
                beforeAction = actionParser.beforeAction,
                afterAction = actionParser.actions,
                printActions = actionParser.printActions,
                api = case["api"],
                case = case,
                timenow = timenow,
                currentCount = i,
                checkActions = actionParser.checkActions,
                purpose = "runsuit",
                suit=suit
            )
            try:
                exec(c)
            except Exception as e:
                info = {"result":False,"errorMsg":"执行用例:%s 出错:%s" %(case["case_name"],str(e))}
                return jsonify(info)

    suit.result["caseCount"] = len(testcases)
    suit.result["apiCount"] = len(suit.orders)
    suit.result["runCount"] = count
    suit = TestSuit(id=suit.id,status=2,result=suit.result)
    db.session.merge(suit)
    db.session.commit()

    s = Template(result_template).render(result=suit.result)
    info["info"] = s
    return jsonify(info)

result_template = """
<span style="color:#FF7F24">测试接口数:{{ result.apiCount }}&nbsp&nbsp&nbsp&nbsp测试用例数:{{ result.caseCount }}&nbsp&nbsp&nbsp&nbsp循环次数:{{ result.runCount }}</span>
{% for index,detail in result.details.items() %}
    <table class="table table-striped" style="width:100%">
        <caption style="text-align:center">第{{ index+1 }}次循环</caption>
        <thead>
            <th class="col-lg-1">接口名</th>
            <th class="col-lg-1">用例名</th>
            <th class="col-lg-3">用例描述</th>
            <th class="col-lg-3">检查点信息</th>
            <th class="col-lg-2" style="text-align:center">成功/失败</th>
            <th class="col-lg-2">日志信息</th>
        </thead>
        <tbody>
            {% for item in detail %}
            <tr class="{% if item.status == 0 %}success{% else %}danger{% endif %}">
                <td>{{ item.apiname }}</td>
                <td><a href="javascript:;" onclick="showcase('{{ item.name }}')">{{ item.name }}</a></td>
                <td>{{ item.desc }}</td>
                <td>
                    {% for fc in item.failCheck %}
                        <li>{{ fc }}</li>
                    {% endfor %}
                    {% for pc in item.passCheck %}
                        <li>{{ pc }}</li>
                    {% endfor %}
                </td>
                <td style="text-align:center">{% if item.status == 0 %}<span style="color:green">成功</span>{% else %}<span style="color:red">失败</span>{% endif %}</td>
                <td><a href="javascript:;" onclick="showlog('{{ item.name }}','{{ item.logpath }}')">查看日志</a></td>
            </tr>
            {% endfor %}
        </tbody>
    </table>
    <hr>
{% endfor %}
"""

@url.route("/showlog")
@login_required
def showlog():
    logpath = request.args.get("logpath")
    realpath = os.path.join(Config.log_path,logpath)
    if os.path.exists(realpath):
        with open(realpath,"r") as f:
            return "<br>".join(f.readlines())
    else:
        return "未找到日志文件"

@url.route("/showcase")
def showcase():
    name = request.args.get("casename")
    case = ApiCase.query.filter_by(name=name).first()
    if case:
        return "<div style='padding:20px'>%s</div>" %"<br>".join(case.content.split("\n"))
    else:
        return "用例不存在或已被删除"