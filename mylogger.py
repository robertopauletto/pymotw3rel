# mylogger

import os
from typing import Union

import logging



logger = logging.getLogger(__name__)
logger.setLevel(logging.DEBUG)
handler = logging.FileHandler('root.log')
formatter = logging.Formatter(
    '%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
handler.setFormatter(formatter)
logger.addHandler(handler)

levels = ("DEBUG", "INFO", "WARNING", "ERROR", "CRITICAL")


def add_module_handler(logger: logging.Logger,
                       level=logging.DEBUG,
                       fmtr: logging.Formatter = formatter,
                       folder: Union[None, str] = None):
    logfilename = f"{logger.name.replace('.', '-')}.log"
    if folder:
        logfilename = os.path.join(folder, logfilename)
    handler = logging.FileHandler(logfilename)
    handler.setLevel(level)
    handler.setFormatter(fmtr)
    logger.addHandler(handler)

