# -*- coding: utf-8 -*-
from flask import Blueprint

url = Blueprint('main',__name__)

from . import apiView,suitView,caseView