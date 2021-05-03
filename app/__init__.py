# __init__.py

import logging
import os

from .settings import DevConfig

from flask import Flask, g
from flask_wtf import CSRFProtect

from app.extensions import db, migrate, ckeditor, Session
from app.models import GeneratorConfig, Article, Category
from app.routes.main import main
from app.site_builder.builder import set_builder_conf


def create_app(fs: str = 'settings.py'):
    app = Flask(__name__)
    cnf = os.getenv('FLASK_ENV')
    if cnf.lower().startswith('dev'):
        app.config.from_object(DevConfig)
    else:
        app.config.from_object(DevConfig)

    crsf = CSRFProtect()
    crsf.init_app(app)

    # Server-side session config
    app.config["SESSION_TYPE"] = 'sqlalchemy'
    app.config["SESSION_PERMANENT"] = True
    app.config['PERMANENT_SESSION_LIFETIME'] = 6000
    app.config["SESSION_USE_SIGNER"] = True
    app.config["SESSION_SQLALCHEMY"] = db
    app.config["SESSION_SQLALCHEMY_TABLE"] = "sessions"
    sess = Session()
    sess.init_app(app)

    ckeditor.init_app(app)
    db.init_app(app)
    migrate.init_app(app, db)

    app.register_blueprint(main)

    # Acquisizione della configurazione per il generatore e altri dati
    # di configurazione
    with app.app_context():
        _, objlist = GeneratorConfig.parse_config()
        diz = dict()
        for obj in objlist:
            diz[obj.conf_key] = obj.conf_value
        set_builder_conf(diz)
    return app

