# -*- coding: utf-8 -*-
from flask import render_template,request,jsonify
from ..models import  db,Api,ApiCase,TestSuit
from jinja2 import Template
from . import url
import json

@url.route("/")
@url.route("/index")
@url.route("/suits")
def index():
    apis = Api.query.all()
    return render_template("suits.html",apis=apis)

@url.route("/newsuit",methods=["POST"])
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
                api = Api.query.filter_by(id=case.api_id).first()
                if api.id not in orderedapi:
                    orders.append({
                        "id":api.id,
                        "name":api.name,
                        "cases":[{"id":c.id,"name":c.name} for c in api.apicases if str(c.id) in suitcases]
                    })
                    orderedapi.append(api.id)
                else:
                    continue
        if orders:
            suit = TestSuit(suitname,json.dumps(orders))
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
        {% for api in orders[suit.id] %}
            <div api-suit-{{suit.id}}="{{api.id}}" class="list-group-item">
                <span class="badge">{{ api.cases|length }}</span>
                <span class="glyphicon glyphicon-move" aria-hidden="true"></span>
                接口:<a href="#suit_{{suit.id}}_api_{{api.id}}" data-toggle="collapse" aria-expanded="false" aria-controls="suit_{{suit.id}}_api_{{api.id}}">{{ api.name }}</a>
                <div class="collapse" id="suit_{{suit.id}}_api_{{api.id}}" style="margin-top:10px">
                    <div id="caselist_suit_{{suit.id}}_api_{{api.id}}" class="list-group">
                    {% for case in api.cases %}
                        <div api-suit-{{suit.id}}-api-{{api.id}}="{{case.id}}" class="list-group-item">
                            <span class="glyphicon glyphicon-move" aria-hidden="true"></span>
                            用例:<span>{{case.name}}</span>
                        </div>
                    {% endfor %}
                    </div>
                </div>
            </div>
        {% endfor %}
        </div>
        <ul class="list-inline list-group">
            <li><button onclick="runsuit({{suit.id}})">运行</button></li>
            <li><button onclick="delsuit({{suit.id}})">删除</button></li>
        </ul>
    </div>
</div>

{% endfor %}
"""

@url.route("/freshsuits")
def freshsuits():
    data = {"suits":None,"orders":None}
    suits = TestSuit.query.all()
    orders = {}
    for suit in suits:
        orders[suit.id] = json.loads(suit.orders)

    s = Template(suit_template).render(
        suits = suits,
        orders = orders
    )

    data["suits"] = s
    data["orders"] = [[suit.id,json.loads(suit.orders)] for suit in suits]

    return jsonify(data)

@url.route("/delsuit/<int:id>",methods=["POST"])
def delsuit(id):
    info = {"result":True,"errorMsg":None}
    try:
        suit = TestSuit.query.filter_by(id=id).first()
        if suit:
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
def updatesuitorder(suitid):
    info = {"result":True,"errorMsg":None}
    neworder = []
    order = dict(request.form).get("api_order[]")
    try:
        suit = TestSuit.query.filter_by(id=suitid).first()
        if suit:
            for apiid in order:
                neworder.append(getitemfromorders(apiid,json.loads(suit.orders)))
            suit.orders = json.dumps(neworder)
            db.session.add(suit)
            db.session.commit()
        else:
            info = {"result":False,"errorMsg":"该测试集不存在或已被删除"}
    except Exception as e:
        info = {"result":False,"errorMsg":str(e)}
    return jsonify(info)

@url.route("/updatecaseorder/<int:suitid>/<int:apiid>",methods=["POST"])
def updatecaseorder(suitid,apiid):
    info = {"result":True,"errorMsg":None}
    caseorder = dict(request.form).get("case_order[]")
    suit = TestSuit.query.filter_by(id=suitid).first()
    neworder = []
    if suit:
        for item in json.loads(suit.orders):
            if item["id"] == apiid:
                newcases = []
                for caseid in caseorder:
                    newcases.append(getitemfromorders(caseid,item["cases"]))
                item["cases"] = newcases
                neworder.append(item)
            else:
                neworder.append(item)

        suit.orders = json.dumps(neworder)
        db.session.add(suit)
        db.session.commit()
    else:
        info = {"result":False,"errorMsg":"该测试集不存在或已被删除"}
    return jsonify(info)

@url.route("/runsuit/<int:id>")
def runsuit(id):
    info = {"result":True,"errorMsg":None}
    suit = TestSuit.query.filter_by(id=id).first()
    testcases = []
    if suit:
        for apiitem in json.loads(suit.orders):
            api = Api.query.filter_by(id=int(apiitem["id"])).first()
            if api:
                for caseitem in apiitem["cases"]:
                    testcases.append([api.name,caseitem["name"]])
            else:
                pass
    else:
        info = {"result":False,"errorMsg":"该测试集不存在或已被删除"}
    print(testcases)
    return jsonify(info)