# -*- coding: utf-8 -*-
from datetime import datetime
from . import db

class Api(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(32))
    url = db.Column(db.String(128))
    type = db.Column(db.String(10))
    reqdata = db.Column(db.PickleType)
    respdata = db.Column(db.PickleType)
    createdtime = db.Column(db.DateTime, default=datetime.now)

    def __init__(self,name,url,type,reqdata=None,respdata=None):
        self.name = name
        self.url = url
        self.type = type
        self.reqdata = reqdata
        self.respdata = respdata

    def __repr__(self):
        return "<API:%s>" % self.name
