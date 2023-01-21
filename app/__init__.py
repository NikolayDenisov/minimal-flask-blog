#!/usr/bin/env python3

import logging
from importlib import import_module

import flask_login
from flask import Flask
from flask_login import LoginManager
from flask_migrate import Migrate
from flask_sqlalchemy import SQLAlchemy

from .models import Users, Posts

app = Flask(__name__, static_folder='base/static')
app.url_map.strict_slashes = False
app.config.from_object('config.Config')
login = LoginManager(app)

db = SQLAlchemy(app)

migrate = Migrate(app, db)
db.create_all()
db.session.commit()


@app.context_processor
def inject_user():
    return dict(user=flask_login.current_user)


def register_blueprints(new_app):
    for module_name in ['admin', 'base']:
        logging.info('register %s', module_name)
        module_obj = import_module('app.{}.routes'.format(module_name))
        new_app.register_blueprint(module_obj.blueprint)


def init_logger():
    """
    Инициализация системы логирования
    :return:
    """
    log_level = logging.DEBUG
    logging.basicConfig(
        format="[%(asctime)s] %(filename)s #%(levelname)-8s %(message)s",
        level=log_level,
        datefmt="%Y-%m-%d %H:%M:%S")
