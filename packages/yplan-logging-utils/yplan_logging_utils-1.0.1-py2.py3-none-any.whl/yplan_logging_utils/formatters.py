# -*- encoding:utf-8 -*-
from __future__ import absolute_import, division, print_function, unicode_literals

import json
import logging
import socket
from datetime import datetime

import six

easy_types = six.string_types + six.integer_types + (bool, dict, float, list)


class PlainJSONFormatter(logging.Formatter):
    """
    Formats records as dicts
    """
    def __init__(self):
        self.host = socket.gethostname()

    def format(self, record):
        message = {
            'host': self.host,
            'levelname': record.levelname,
            'logger': record.name,
            'message': record.getMessage(),
            'time': datetime.utcnow().isoformat(),
        }

        message.update(self.get_extra_fields(record))

        if record.exc_info:
            message.update(self.get_debug_fields(record))

        return message

    def get_extra_fields(self, record):
        # The list contains all the attributes listed in
        # http://docs.python.org/library/logging.html#logrecord-attributes
        skip_list = (
            'args', 'asctime', 'created', 'exc_info', 'exc_text', 'filename',
            'funcName', 'id', 'levelname', 'levelno', 'lineno', 'module',
            'msecs', 'msecs', 'message', 'msg', 'name', 'pathname', 'process',
            'processName', 'relativeCreated', 'thread', 'threadName', 'extra'
        )

        fields = {}

        for key, value in record.__dict__.items():
            if key not in skip_list:
                if isinstance(value, easy_types) or value is None:
                    fields[key] = value
                else:
                    fields[key] = repr(value)

        return fields

    def get_debug_fields(self, record):
        return {
            'exc_info': self.formatException(record.exc_info),
            'lineno': record.lineno,
            'process': record.process,
            'threadName': record.threadName,
            'funcName': record.funcName,
            'processName': record.processName,
        }


class JSONFormatter(PlainJSONFormatter):

    def format(self, record):
        message = super(JSONFormatter, self).format(record)
        return json.dumps(message)
