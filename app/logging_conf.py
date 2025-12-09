# app/logging_conf.py
import logging
from logging.config import dictConfig

def setup_logging():
    dictConfig({
        "version": 1,
        "disable_existing_loggers": False,
        "formatters": {
            "default": {
                "format": "[%(asctime)s] [%(levelname)s] [%(name)s] %(message)s",
            }
        },
        "handlers": {
            "console": {
                "class": "logging.StreamHandler",
                "formatter": "default"
            }
        },
        "loggers": {
            "app": {      # ROOT logger dla całej aplikacji
                "handlers": ["console"],
                "level": "INFO",
                "propagate": False
            },
            "app.loader": {
                "handlers": ["console"],
                "level": "DEBUG",
                "propagate": False
            },
            "app.routing": {
                "handlers": ["console"],
                "level": "INFO",
                "propagate": False
            },
            "app.api": {
                "handlers": ["console"],
                "level": "INFO",
                "propagate": False
            }
        }
    })
