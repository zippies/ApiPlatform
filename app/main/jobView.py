# -*- coding: utf-8 -*-
from flask import render_template
from ..models import  db,Api,ApiCase
from . import url

@url.route("/")
@url.route("/index")
@url.route("/jobs")
def index():
    apis = Api.query.all()
    return render_template("jobs.html",apis=apis)
