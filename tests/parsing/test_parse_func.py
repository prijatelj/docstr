"""Tests of the compiler-like checking of docstrings to ensure they parse
styles as they are expected and includes examples of out-of-style
docstrings.
"""
from collections import OrderedDict
from types import FunctionType

import pytest

from docstr import docstring, parse

import testing.numpy_example_docstrings as examples


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
        return_doc=BaseDoc(
            'Returns',
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
    expected_func_defaults.args['foo'].choices = choices
    expected_func_defaults.args['bar'].choices = choices
    return expected_func_defaults


@pytest.mark.dependency(name='TestParseFunc')
class TestParseFunc:
    @pytest.mark.dependency(name='TestParseFunc.func')
    def test_docstr_parse_func(expected_func):
        parsed = parse('numpy', examples.numpy_doc_func)
        assert expected == parsed

    @pytest.mark.dependency(
        name='TestParseFunc.defaults',
        defaults=['TestParseFunc.func'],
    )
    def test_docstr_parse_func_defaults(expected_func_defaults):
        parsed = parse('numpy', examples.numpy_doc_func_defaults)
        assert expected_func_defaults == parsed

    @pytest.mark.dependency(
        name='TestParseFunc.choices',
        defaults=['TestParseFunc.defaults'],
    )
    def test_docstr_parse_func_choices(expected_func_choices):
        parsed = parse('numpy', examples.numpy_doc_func_choices)
        assert expected_func_choices == parsed
