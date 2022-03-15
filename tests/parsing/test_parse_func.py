"""Tests of the compiler-like checking of docstrings to ensure they parse
styles as they are expected and includes examples of out-of-style
docstrings.
"""
from collections import OrderedDict
from types import FunctionType

import pytest

from docstr import docstring, parse

import tests.numpy_example_docstrings as examples


@pytest.fixture
def expected_func():
    return docstring.FuncDocstring(
        examples.numpy_doc_func.__name__,
        FunctionType,
        'This is the short desc. of the function, concat the paired strings',
        args=OrderedDict(
            foo=docstring.ArgDoc(
                'foo',
                str,
                'Foo is an excellently documented string argument.',
            ),
            bar=docstring.ArgDoc(
                'bar',
                str,
                'Bar is an excellently documented string argument.',
            )
        ),
        returns=docstring.BaseDoc(
            'returns',
            str,
            'An incredible ordered concatenation of the paired string inputs.',
        )
    )


@pytest.fixture
def expected_func_defaults(expected_func):
    expected_func.args['foo'].default = 'foo'
    expected_func.args['bar'].default = 'bar'
    return expected_func


@pytest.fixture
def expected_func_choices(expected_func_defaults):
    choices = docstring.MultiType({'foo', 'bar'})
    expected_func_defaults.args['foo'].type = choices
    expected_func_defaults.args['bar'].type = choices
    return expected_func_defaults


@pytest.mark.incremental
class TestParseFunc:
    def test_docstr_parse_func(expected_func):
        parsed = parse(examples.numpy_doc_func, 'numpy')
        assert expected_func == parsed

    def test_docstr_parse_func_defaults(expected_func_defaults):
        parsed = parse(examples.numpy_doc_func_defaults, 'numpy')
        assert expected_func_defaults == parsed

    def test_docstr_parse_func_choices(expected_func_choices):
        parsed = parse(examples.numpy_doc_func_choices, 'numpy')
        assert expected_func_choices == parsed
