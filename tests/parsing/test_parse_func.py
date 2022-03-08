"""Tests of the compiler-like checking of docstrings to ensure they parse
styles as they are expected and includes examples of out-of-style
docstrings.
"""
from collections import OrderedDict
from types import FunctionType

from docstr import docstring, parse

import testing.numpy_example_docstrings as examples

# TODO given tests/numpy_example_docstrings.py, parse the docstrings and check
# the resulting parsed docstring objects.

# TODO pytest hook to setup the common dependencies behind these tests. Write
# once, after all...

def test_docstr_parse_func():
    # Create the expected result of docstring.
    expected = docstring.FuncDocstring(
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

    # Decide if parser is function or class object.
    parsed = parse(examples.numpy_doc_func)

    # Comparison supported betweend the docstr.docstring classes.
    assert expected == parsed
