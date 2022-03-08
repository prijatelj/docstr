"""Tests of the compiler-like checking of docstrings to ensure they parse
styles as they are expected and includes examples of out-of-style docstrings.
"""
from collections import OrderedDict
from types import FunctionType

import pytest

from docstr import docstring, parse

import testing.numpy_example_docstrings as examples
from testing.parsing.test_parse_class_with_primitives import (
    TestParseClassPrimitives,
    expected_class_of_primitives,
)


@pytest.fixture
def expected_class_linking(expected_class_of_primitives):
    expected_class_of_primitives.attributes.update(
        example_var=docstring.ArgDoc('example_var', object),
        is_this_correct=docstring.ArgDoc(
            'is_this_correct',
            bool,
            default=False,
        ),
    )
    expected_class_of_primitives.methods.update(
        bar=FuncDocstring(
            'bar',
            FunctionType,
            'Same args as foo, but performs a different operation.',
            args=expected_class_of_primitives.methods['foo'].args
        )
    )
    return docstring.ClassDocstring(
        examples.NumpyDocClassLinkning.__name__,
        examples.NumpyDocClassLinkning,
        'A Numpy example class that uses docstring linking.',
        attributes=expected_class_of_primitives.attributes,
        methods=expected_class_of_primitives.methods,
    )


class TestParseClassLinking(TestParseClassPrimitives):
    @pytest.mark.dependency(
        name='TestParseClassLinking',
        depends=['TestParseClassPrimitives'],
    )
    def test_class_doc_linking(expected_class_linking):
        parsed = parse('numpy', examples.NumpyDocClassLinking)
        assert expected_class_linking == parsed
