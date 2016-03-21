# -*- coding: utf-8 -*-
import os

class Config:
    DEBUG = True
    SQLALCHEMY_DATABASE_URI = "mysql+pymysql://root:%s@%s:3306/ApiAutomationPlatform" %(os.environ.get("MYSQL_PASSWORD"),os.environ.get("HOST_NAME"))
    #SQLALCHEMY_DATABASE_URI = "sqlite:///" + os.path.join(os.path.abspath(os.path.dirname(__file__)),'data.sqlite')
    SECRET_KEY = 'what does the fox say?'
    WTF_CSRF_SECRET_KEY = "whatever"
    UPLOAD_FOLDER = os.path.join(os.path.dirname(__file__),"app/static")
    SQLALCHEMY_TRACK_MODIFICATIONS = True
    log_path = os.path.join(os.path.dirname(__file__),"logs")

    @staticmethod
    def init_app(app):
        pass
