# __init__.py

import logging
import os

from .settings import DevConfig

from flask import Flask, g


from app.extensions import db, migrate, ckeditor
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

