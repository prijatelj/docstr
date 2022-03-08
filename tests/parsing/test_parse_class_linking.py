"""Tests of the compiler-like checking of docstrings to ensure they parse
styles as they are expected and includes examples of out-of-style
docstrings.
"""
from collections import OrderedDict
from types import FunctionType

import pytest

from docstr import docstring, parse

import testing.numpy_example_docstrings as examples
from testing.parsing.test_parse_class_with_primitives import \
    TestParseClassPrimitives


class TestParseClassLinking(TestParseClassPrimitives):
    @pytest.mark.dependency(
        name='TestParseClassLinking',
        depends=['TestParseClassPrimitives'],
    )
    def test_class_doc_linking():
        # TODO use the given pre-made hook expected item.
        # TODO Create the expected result of docstring.

        # Decide if parser is function or class object.
        parsed = parse(examples.NumpyDocClassLinking)

        # Comparison supported betweend the docstr.docstring classes.
        assert expected == parsed
