"""Tests of the compiler-like checking of docstrings to ensure they parse
styles as they are expected and includes examples of out-of-style
docstrings.
"""
from collections import OrderedDict
#from collections.abc import Callable
#import inspect
from types import FunctionType

from docstr import docstring, parsing

import testing.numpy_example_docstrings as examples

# TODO given tests/numpy_example_docstrings.py, parse the docstrings and check
# the resulting parsed docstring objects.

# TODO pytest hook to setup the common dependencies behind these tests. Write
# once, after all...

def test_docstr_parse_func():
    short_desc = \
        'This is the short desc. of the function, concat the paired strings'

    # Create the expected result of parsing.
    expected = docstring.FuncDocstring(
        'numpy_doc_func',
        short_desc,
        FunctionType,
        short_desc,
        args=OrderedDict(
            foo=parsing.ArgDoc(
                'foo',
                'Foo is an excellently documented string argument.',
                str,
            ),
            bar=parsing.ArgDoc(
                'bar',
                'Bar is an excellently documented string argument.',
                str,
            )
        ),
        return_doc=BaseDoc(
            'Returns',
            'An incredible ordered concatenation of the paired string inputs.',
            str,
        )
    )

    # TODO Decide if parser is function or class object.
    parsed = docstr.parsing.parse(examples.numpy_doc_func)

    # TODO Comparison supported betweend the docstr.docstring classes.
    assert expected == parsed


def test_class_of_primitives():
    # TODO Create the expected result of parsing.

    # TODO Decide if parser is function or class object.
    parsed = docstr.parsing.parse(examples.NumpyDocClass)

    # TODO Comparison supported betweend the docstr.docstring classes.
    assert expected == parsed


def test_class_doc_linking():
    # TODO Create the expected result of parsing.

    # TODO Decide if parser is function or class object.
    parsed = docstr.parsing.parse(examples.NumpyDocClassLinking)

    # TODO Comparison supported betweend the docstr.docstring classes.
    assert expected == parsed

def test_class_doc_2hop_linking_and_non_primitive_arg():
    # TODO Create the expected result of parsing.

    # TODO Decide if parser is function or class object.
    parsed = docstr.parsing.parse(examples.NumpyDocClassMultiLinking)

    # TODO Comparison supported betweend the docstr.docstring classes.
    assert expected == parsed
