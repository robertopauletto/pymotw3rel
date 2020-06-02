import logging.config
import os
from typing import Type

from dotenv import load_dotenv

from mylogger import add_module_handler
from app import create_app
from app.settings import DevConfig, Config

__doc__ = 'Punto di entrata della procedura'

logger = logging.getLogger('launcher')
logger.setLevel(logging.DEBUG)
add_module_handler(logger, folder='logs')


if __name__ == '__main__':
    try:
        myapp = create_app()
        logger.info('App creata')
        logger.info(f'Ambiente: {os.getenv("FLASK_ENV")}')
        myapp.run(debug=True)
    except Exception as exc:
        print(exc)
        logger.exception(exc)
