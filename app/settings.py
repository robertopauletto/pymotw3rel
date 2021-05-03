# settings.py

import os

from dotenv import load_dotenv

__doc__ = 'Configuration for app'

load_dotenv()

# SECRET_KEY = os.environ.get('SECRET_KEY')
# HTML Generator JSON config file
# SQLALCHEMY_TRACK_MODIFICATIONS = os.getenv('SQLALCHEMY_MODIFICATIONS')
# SQLALCHEMY_DATABASE_URI = os.getenv('SQLALCHEMY_DATABASE_URI')


class Config:
    SECRET_KEY = os.environ.get('SECRET_KEY')
    # HTML Generator JSON config file
    HTML_GEN_CONFIG = 'site_builder_config.json'
    CKEDITOR_ENABLE_CODESNIPPET = True
    # SERVER_NAME = 'local.dev:5000'


class DevConfig(Config):
    SQLALCHEMY_TRACK_MODIFICATIONS = os.getenv('SQLALCHEMY_MODIFICATIONS')
    SQLALCHEMY_DATABASE_URI = os.getenv('SQLALCHEMY_DATABASE_URI')
    HTML_GEN_CONFIG = 'site_builder_config.json'
    ARTICLES_PER_PAGE = 10
