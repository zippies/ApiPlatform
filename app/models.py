# -*- coding: utf-8 -*-
from datetime import datetime
from collections import OrderedDict
from flask_login import UserMixin
from . import db,login_manager

info = {"result":True,"errorMsg":None}
message = {"type":"info","message":None}

@login_manager.user_loader
def load_user(user_id):
    return User.query.filter_by(id=user_id).first()


login_manager.session_protection = "strong"
login_manager.login_view = "main.login"
login_manager.login_message = {"type":"error","message":"请登录后使用该功能"}


class User(db.Model,UserMixin):
    id = db.Column(db.Integer,primary_key=True)
    nickname = db.Column(db.String(32))
    sex = db.Column(db.String(10))
    phonenum = db.Column(db.String(32),unique=True,index=True)
    email = db.Column(db.String(32),unique=True,index=True)
    password = db.Column(db.String(128))
    password_heihei = db.Column(db.String(2048))
    ip = db.Column(db.String(32))
    apis = db.relationship('Api', backref='user', lazy='dynamic')
    suits = db.relationship('TestSuit', backref='user', lazy='dynamic')
    cases = db.relationship('ApiCase', backref='user', lazy='dynamic')
    createdtime = db.Column(db.DateTime,default=datetime.now)

    def __init__(self,nickname,phonenum,password,password_heihei,email,sex,ip):
        self.nickname = nickname
        self.phonenum = phonenum
        self.email = email
        self.password = password
        self.password_heihei = password_heihei
        self.sex = sex
        self.ip = ip

    def __repr__(self):
        return "<User:%s>" %self.nickname


class Api(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(32))
    url = db.Column(db.String(128))
    type = db.Column(db.String(10))
    headers = db.Column(db.PickleType)
    reqdata = db.Column(db.PickleType)
    respdata = db.Column(db.PickleType)
    apicases = db.relationship('ApiCase', backref='api', lazy='dynamic')
    userid = db.Column(db.Integer, db.ForeignKey('user.id'))
    createdtime = db.Column(db.DateTime, default=datetime.now)

    def __init__(self,name,url,type,userid,headers={},reqdata=None,respdata=None):
        self.name = name
        self.url = url
        self.type = type
        self.userid = userid
        self.headers = headers
        self.reqdata = reqdata
        self.respdata = respdata

    @property
    def casecount(self):
        count = 0
        for case in self.apicases:
            count += 1
        return count

    def __repr__(self):
        return "<Api:%s belong userid:%s>" % (self.name,self.userid)

class ApiCase(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(32))
    desc = db.Column(db.String(256))
    content = db.Column(db.PickleType)
    apiid = db.Column(db.Integer,db.ForeignKey('api.id'))
    userid = db.Column(db.Integer, db.ForeignKey('user.id'))

    def __init__(self,name,desc,content,userid):
        self.name = name
        self.desc = desc
        self.content = content
        self.userid = userid

    @property
    def api(self):
        return Api.query.filter_by(id=self.apiid).first()

    def __repr__(self):
        return "<ApiCase:%s belong apiid:%s>" %(self.name,self.apiid)

class TestSuit(db.Model):
    id = db.Column(db.Integer,primary_key=True)
    name = db.Column(db.String(32))
    orders = db.Column(db.PickleType)
    status = db.Column(db.Integer,default=0)
    result = db.Column(db.PickleType,default={"caseCount":0,"apiCount":0,"runCount":1,"details":OrderedDict()})
    userid = db.Column(db.Integer, db.ForeignKey('user.id'))
    createdtime = db.Column(db.DateTime, default=datetime.now)

    def __repr__(self):
        return "<TestSuit:%s belong userid:%s>" % (self.name,self.userid)