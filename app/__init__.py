# __init__.py

import logging

from flask import Flask

from app.extensions import db
from app.models import GeneratorConfig
from app.routes.main import main
from app.site_builder.builder import set_builder_conf


logger = logging.getLogger(__name__)
logger.setLevel(logging.DEBUG)
handler = logging.FileHandler('root.log')
logger.addHandler(handler)

levels = ("DEBUG", "INFO", "WARNING", "ERROR", "CRITICAL")


def add_module_handler(logger: logging.Logger, level=logging.DEBUG):
    handler = logging.FileHandler(f"{logger.name.replace('.', '-')}.log")
    handler.setLevel(level)
    logger.addHandler(handler)


def create_app(config_file: str = 'settings.py'):
    app = Flask(__name__)
    app.config.from_pyfile(config_file)
    db.init_app(app)

    app.register_blueprint(main)
    with app.app_context():
        _, objlist = GeneratorConfig.parse_config()
        diz = dict()
        for obj in objlist:
            diz[obj.conf_key] = obj.conf_value
        set_builder_conf(diz)
    return app

