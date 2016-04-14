# -*- coding: utf-8 -*-
from flask import render_template
from . import url

@url.route("/")
@url.route("/index")
@url.route("/jobs")
def index():
    return render_template("jobs.html")
