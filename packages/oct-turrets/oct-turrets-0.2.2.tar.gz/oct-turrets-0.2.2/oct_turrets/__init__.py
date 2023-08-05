import logging.config

from oct_turrets.config import LOGGING_CONFIG

__version__ = '0.2.2'


logging.config.dictConfig(LOGGING_CONFIG)
