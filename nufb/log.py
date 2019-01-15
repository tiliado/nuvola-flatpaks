# Copyright 2019 Jiří Janoušek <janousek.jiri@gmail.com>
# License: BSD-2-Clause, see file LICENSE at the project root.

"""Logging set-up."""

import logging


LOGGING_CONFIG = dict(
    version=1,
    disable_existing_loggers=False,
    formatters={
        'standard': {
            'format': '•[%(asctime)s %(name)-15s] %(levelname)s %(message)s ¶',
            'datefmt': '%H:%M:%S',
        },
    },
    handlers={
        'default': {
            'class': 'logging.StreamHandler',
            'formatter': 'standard',
            'level': 'DEBUG',
        },
    },
    loggers={
        '': {
            'handlers': ['default'],
            'level': 'DEBUG',
            'propagate': True,
        },
    }
)


def get_logger(name: str) -> logging.Logger:
    """
    Create new logger.

    :param name: The logger domain.
    :return: New logger.
    """
    return logging.getLogger(name)


def set_up_logging():
    """Set up logging."""
    from logging.config import dictConfig
    dictConfig(LOGGING_CONFIG)
