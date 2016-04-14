# -*- coding: utf-8 -*-
from flask import render_template,request,jsonify
from .framework.main import support_methods,send_request
from ..models import db,Api
from config import Config
from jinja2 import Template
from . import url

@url.route("/cases")
def cases():
    apis = Api.query.all()
    return render_template("cases.html",apis=apis,support_methods=support_methods)

@url.route("/runscript",methods=["POST"])
def runscript():
    info = {"result":True,"errorMsg":None}
    id = int(request.form.get("id"))
    api = Api.query.filter_by(id=id).first()

    script = request.form.get("script").strip()
    case = Template(Config.case_template).render(
        codes = script.split("\r\n"),
        api = api,
        data = api.reqdata,
        headers = {},
        timeout = (2,5)
    )
    print(case)
    exec(case)

    return jsonify(info)
