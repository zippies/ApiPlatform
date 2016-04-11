# -*- coding: utf-8 -*-
from flask import render_template
from .framework.main import support_methods
from . import main

@main.route("/cases")
def cases():
    return render_template("cases.html",support_methods=support_methods)
