# settings.py

import os

from dotenv import load_dotenv

__doc__ = 'Configuration for app'

load_dotenv()

SQLALCHEMY_DATABASE_URI = os.getenv('SQLALCHEMY_DATABASE_URI')
SQLALCHEMY_TRACK_MODIFICATIONS = os.getenv('SQLALCHEMY_MODIFICATIONS')
SECRET_KEY = os.environ.get('SECRET_KEY')
# HTML Generator JSON config file
HTML_GEN_CONFIG = 'site_builder_config.json'

