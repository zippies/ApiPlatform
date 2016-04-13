# -*- coding: utf-8 -*-
from flask import render_template
from . import main

@main.route("/")
@main.route("/index")
@main.route("/jobs")
def index():
    return render_template("jobs.html")
