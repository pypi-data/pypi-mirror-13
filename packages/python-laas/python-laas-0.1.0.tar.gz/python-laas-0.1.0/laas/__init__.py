# -*- coding: utf-8 -*-
from functools import partial, wraps
import logging
import os

from logging import (NOTSET, DEBUG, INFO, WARNING, ERROR, CRITICAL)
from logstash_formatter import LogstashFormatterV1

handler = logging.StreamHandler()
formatter = LogstashFormatterV1()
handler.setFormatter(formatter)
handler.setLevel(INFO)

logger = logging.getLogger()
logger.addHandler(handler)
logger.setLevel(INFO)

extras = {
    "logType": os.getenv("LAAS_LOG_TYPE", ""),
    "host": os.getenv("MICROS_SERVICE_DOMAIN_NAME", ""),
}

def inject_extras(f, *args, **kwargs):
    @wraps(f)
    def wrapper(msg, *args, **kwargs):
        kwargs.setdefault("extra", {}).update(extras)
        return f(msg, *args, **kwargs)
    return wrapper

critical = inject_extras(logger.critical)
debug = inject_extras(logger.debug)
error = inject_extras(logger.error)
exception = inject_extras(logger.exception)
fatal = inject_extras(logger.fatal)
info = inject_extras(logger.info)
log = inject_extras(logger.log)
warn = inject_extras(logger.warn)
warning = inject_extras(logger.warning)
