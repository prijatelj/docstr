"""Tests of the compiler-like checking of docstrings to ensure they parse
styles as they are expected and includes examples of out-of-style
docstrings.

The fixtures are the expected parsed tokens from docstr.parse.
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
    expected_func.name = examples.numpy_doc_func_defaults.__name__
    expected_func.args['foo'].default = 'foo'
    expected_func.args['bar'].default = 'bar'
    return expected_func


@pytest.fixture
def expected_func_choices(expected_func_defaults):
    expected_func_defaults.name = examples.numpy_doc_func_choices.__name__
    choices = docstring.MultiType({'foo', 'bar'})
    expected_func_defaults.args['foo'].type = choices
    expected_func_defaults.args['bar'].type = choices
    return expected_func_defaults


@pytest.fixture
def expected_func_alt_defaults(expected_func_defaults):
    expected_func_defaults.name = examples.numpy_doc_func_alt_defaults.__name__
    return expected_func_defaults


@pytest.fixture
def expected_func_linking(expected_func_defaults):
    expected_func_defaults.name = examples.numpy_doc_func_linking.__name__
    return expected_func_defaults


@pytest.fixture
def expected_func_linking_arg_pass_thru(expected_func_defaults):
    expected_func_defaults.name = \
        examples.numpy_doc_func_linking_arg_pass_thru.__name__
    expected_func_defaults.args['bar'].type = docstring.MultiType(
        {'foo', 'bar'},
    )
    return expected_func_defaults


@pytest.fixture
def expected_func_linking_args(expected_func_defaults):
    expected_func_defaults.name = examples.numpy_doc_func_linking_args.__name__

    expected_func_defaults.args['boo'] = expected_func_defaults.args['foo']
    expected_func_defaults.args['boo'].name = 'boo'

    expected_func_defaults.args['far'] = expected_func_defaults.args['bar']
    expected_func_defaults.args['far'].type = docstring.MultiType(
        {'foo', 'bar'},
    )

    del expected_func_defaults.args['foo'], expected_func_defaults.args['bar']

    return expected_func_defaults


@pytest.fixture
def expected_func_linking_see_end(expected_func_defaults):
    expected_func_defaults.name = examples.numpy_doc_func_linking_see_end.__name__
    expected_func_defaults.returns.description = \
        'An incredible ordered concatenation of the ordered string inputs.'
    desc = 'An excellently documented string argument.'

    new_args = OrderedDict(
        fizz=docstring.ArgDoc('fizz', str, desc),
        buzz=docstring.ArgDoc(
            'buzz',
            docstring.MultiType({'fizz', 'buzz'}),
            desc,
        ),
    )
    new_args.update(expected_func_defaults.args)
    expected_func_defaults.args = new_args

    return expected_func_defaults


@pytest.fixture
def expected_func_linking_see_start(expected_func_defaults):
    expected_func_defaults.name = examples.numpy_doc_func_linking_see_start.__name__
    expected_func_defaults.returns.description = \
        'An incredible ordered concatenation of the ordered string inputs.'
    desc = 'An excellently documented string argument.'

    new_args = OrderedDict(
        fizz=docstring.ArgDoc('fizz', str, desc, 'fizz'),
        buzz=docstring.ArgDoc(
            'buzz',
            docstring.MultiType({'fizz', 'buzz'}),
            desc,
            'buzz',
        ),
    )
    expected_func_defaults.args.update(new_args)

    return expected_func_defaults


@pytest.fixture
def expected_func_linking_see_mid(expected_func_defaults):
    expected_func_defaults.name = examples.numpy_doc_func_linking_see_mid.__name__
    expected_func_defaults.returns.description = \
        'An incredible ordered concatenation of the ordered string inputs.'
    desc = 'An excellently documented string argument.'

    new_args = OrderedDict(fizz=docstring.ArgDoc('fizz', str, desc))

    new_args.update(expected_func_defaults.args)

    new_args['buzz'] = docstring.ArgDoc(
        'buzz',
        docstring.MultiType({'fizz', 'buzz'}),
        desc,
        'buzz',
    )
    expected_func_defaults.args = new_args

    return expected_func_defaults


@pytest.mark.dependency(name='parse_defaults_choices', scope='session')
@pytest.mark.incremental
class TestParseFunc:
    """The fundamental parsing of functions including defaults and choices."""
    def test_docstr_parse_func(self, expected_func):
        parsed = parse(examples.numpy_doc_func, 'numpy')
        assert expected_func == parsed

    def test_docstr_parse_func_defaults(self, expected_func_defaults):
        parsed = parse(examples.numpy_doc_func_defaults, 'numpy')
        assert expected_func_defaults == parsed

    def test_docstr_parse_func_choices(self, expected_func_choices):
        parsed = parse(examples.numpy_doc_func_choices, 'numpy')
        assert expected_func_choices == parsed


@pytest.mark.dependency(depends=['parse_defaults_choices'])
@pytest.mark.xfail
def test_func_alt_defaults(self, expected_func_alt_defaults):
    parsed = parse(examples.numpy_doc_func_alt_defaults, 'numpy')
    assert expected_func_alt_defaults == parsed


@pytest.mark.dependency(depends=['parse_defaults_choices'])
class TestParseFuncDocLinking:
    def test_docstr_parse_func_linking(self, expected_func_linking):
        parsed = parse(examples.numpy_doc_func_linking, 'numpy')
        assert expected_func_linking == parsed

    def test_docstr_parse_func_linking_arg_pass_thru(
        self,
        expected_func_linking_arg_pass_thru,
    ):
        parsed = parse(examples.numpy_doc_func_linking_arg_pass_thru, 'numpy')
        assert expected_func_linking_arg_pass_thru == parsed

    def test_docstr_parse_func_linking_args(self, expected_func_linking_args):
        parsed = parse(examples.numpy_doc_func_linking_args, 'numpy')
        assert expected_func_linking_args == parsed

    def test_func_linking_see_end(self, expected_func_linking_see_end):
        parsed = parse(examples.numpy_doc_func_linking_see_end, 'numpy')
        assert expected_func_linking_see_end == parsed

    def test_func_linking_see_start(self, expected_func_linking_see_start):
        parsed = parse(examples.numpy_doc_func_linking_see_start, 'numpy')
        assert expected_func_linking_see_start == parsed

    def test_func_linking_see_mid(self, expected_func_linking_see_mid):
        parsed = parse(examples.numpy_doc_func_linking_see_mid, 'numpy')
        assert expected_func_linking_see_mid == parsed
