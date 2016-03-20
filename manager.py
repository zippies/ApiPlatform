# -*- coding: utf-8 -*-
from app import createApp,db
from app.models import *
from flask.ext.script import Manager,Shell
from flask.ext.migrate import Migrate,MigrateCommand
from werkzeug.contrib.fixers import ProxyFix
import os

app = createApp()
app.debug = True
app.wsgi_app = ProxyFix(app.wsgi_app)
manager = Manager(app)
migrate = Migrate(app,db)
manager.add_command('db',MigrateCommand)

@manager.command
def dbinit():
	db.create_all()
	print('dbinit ok')

@manager.command
def dbdrop():
	db.drop_all()
	print('ok')

if __name__ == '__main__':
	manager.run()