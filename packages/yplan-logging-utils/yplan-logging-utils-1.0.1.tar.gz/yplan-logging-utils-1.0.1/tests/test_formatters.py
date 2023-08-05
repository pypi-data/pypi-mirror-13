# -*- encoding:utf-8 -*-
from __future__ import absolute_import, division, print_function, unicode_literals

import json
import socket
from logging import INFO, LogRecord

import pytest
from yplan_logging_utils.formatters import JSONFormatter, PlainJSONFormatter


@pytest.fixture
def plain_json_formatter():
    return PlainJSONFormatter()


@pytest.fixture
def json_formatter():
    return JSONFormatter()


def assert_contains(dicty, subset):
    for key in subset:
        assert dicty[key] == subset[key]


def assert_contains_keys(dicty, keys):
    assert (set(keys) - set(dicty.keys())) == set()


def test_plain_json_formatter_basic(plain_json_formatter):
    record = LogRecord(
        name='test',
        level=INFO,
        pathname='/test.py',
        lineno=1337,
        msg="This is a test",
        args=[],
        exc_info=None
    )
    actual = plain_json_formatter.format(record)
    assert_contains(actual, {
        'message': 'This is a test',
        'host': socket.gethostname(),
        'levelname': 'INFO',
        'logger': 'test',
    })
    assert_contains_keys(actual, {'time'})


def test_json_formatter_basic(json_formatter):
    record = LogRecord(
        name='test',
        level=INFO,
        pathname='/test.py',
        lineno=1337,
        msg="This is a test",
        args=[],
        exc_info=None
    )
    formatted = json_formatter.format(record)
    actual = json.loads(formatted)
    assert_contains(actual, {
        'message': 'This is a test',
        'host': socket.gethostname(),
        'levelname': 'INFO',
        'logger': 'test',
    })
    assert_contains_keys(actual, {'time'})


def test_json_formatter_easy_extra_types(json_formatter):
    record = LogRecord(
        name='test', level=INFO, pathname='/test.py', lineno=1337, msg="This is a test", args=[], exc_info=None
    )
    record.extra_one = 'String Test'
    record.extra_two = 1092384901283490120984
    record.extra_three = ['list test']
    actual = json.loads(json_formatter.format(record))
    assert_contains(actual, {
        'extra_one': 'String Test',
        'extra_two': 1092384901283490120984,
        'extra_three': ['list test'],
    })


def test_json_formatter_non_easy_extra_types(json_formatter):
    record = LogRecord(
        name='test', level=INFO, pathname='/test.py', lineno=1337, msg="This is a test", args=[], exc_info=None
    )

    class Example(object):
        def __repr__(self):
            return 'Example Repr in action!'
    record.extra_one = Example()

    actual = json.loads(json_formatter.format(record))
    assert_contains(actual, {
        'extra_one': 'Example Repr in action!',
    })
