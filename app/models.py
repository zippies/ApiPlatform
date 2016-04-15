# -*- coding: utf-8 -*-
from datetime import datetime
from . import db

class Api(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(32),unique=True)
    url = db.Column(db.String(128))
    type = db.Column(db.String(10))
    headers = db.Column(db.PickleType)
    reqdata = db.Column(db.PickleType)
    respdata = db.Column(db.PickleType)
    apicases = db.relationship('ApiCase', backref='api', lazy='dynamic')
    createdtime = db.Column(db.DateTime, default=datetime.now)

    def __init__(self,name,url,type,headers={},reqdata=None,respdata=None):
        self.name = name
        self.url = url
        self.type = type
        self.headers = headers
        self.reqdata = reqdata
        self.respdata = respdata

    def __repr__(self):
        return "<API:%s>" % self.name

class ApiCase(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(32),unique=True)
    desc = db.Column(db.String(256))
    content = db.Column(db.PickleType)
    api_id = db.Column(db.Integer,db.ForeignKey('api.id'))

    def __init__(self,name,desc,content):
        self.name = name
        self.desc = desc
        self.content = content