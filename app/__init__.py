# -*- coding: utf-8 -*-
from flask import Flask
from flask.ext.sqlalchemy import SQLAlchemy
from flask.ext.login import LoginManager
from flask.ext.bootstrap import Bootstrap
from flask.ext.script import Manager
# 
# import logging
# from logging.handlers import RotatingFileHandler
# from logging import Formatter

app = Flask(__name__) 
app.config.from_object('config.ProductConfig')

# file_handler = RotatingFileHandler('logs/app.log', maxBytes=102400, backupCount=5)
# if app.config['DEBUG']:
#     file_handler.setLevel(logging.DEBUG)
# else:
#     file_handler.setLevel(logging.WARNING)
# file_handler.setFormatter(Formatter('%(asctime)s %(levelname)s:\n\t%(message)s\n\t'
#                                     '[in %(pathname)s:%(lineno)d]'))
# app.logger.addHandler(file_handler)

db = SQLAlchemy(app)

bootstrap = Bootstrap(app)

login_manager = LoginManager(app)
login_manager.session_protection = 'strong'
login_manager.login_view = '/login'

app.debug = True

import models
models.create_db()

from speaking import views as speaking_views
from auth import views as auth_views
from main import views as main_views
from admin import views as admin_views
from writing import views as writing_views

@app.after_request
def add_header(response):
    response.cache_control.max_age = 0
    # print response.content_type
    # print response.cache_control
    return response
