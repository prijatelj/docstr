"""Tests of the compiler-like checking of docstrings to ensure they parse
styles as they are expected and includes examples of out-of-style
docstrings.
"""
from collections import OrderedDict
from types import FunctionType

import pytest

from docstr import docstring, parse

import testing.numpy_example_docstrings as examples
from testing.parsing.test_parse_func import TestParseFunc


class TestParseClassPrimitives(TestParseFunc):
    @pytest.mark.dependency(
        name='TestParseClassPrimitives',
        depends=['TestParseFunc'],
    )
    def test_class_of_primitives():
        """Tests the example class of primitives, but also includes attribute as
        init arg inherent pass through, which only works when not using meta splat
        expansion.
        """
        # Create the expected result of docstring.
        name_doc = docstring.ArgDoc(
            'name',
            str,
            'Foo is an excellently documented string argument.',
        )
        z_doc = docstring.ArgDoc(
            'z',
            float,
            'Foo is an excellently documented string argument.',
        )
        int_float = MultiType({int, float}),

        expected = docstring.ClassDocstring(
            examples.NumpyDocClass.__name__,
            examples.NumpyDocClass,
            'This is an example class with Numpy docstrings. Short description ends.',
            attributes=OrderedDict(
                name_doc,
                a_plus_b=docstring.ArgDoc(
                    'a_plus_b',
                    int_float,
                    'Foo is an excellently documented string argument.',
                ),
                x_times_y=docstring.ArgDoc(
                    'x_times_y',
                    float,
                    'Foo is an excellently documented string argument.',
                ),
                c=docstring.ArgDoc(
                    'c',
                    int_float,
                    'Foo is an excellently documented string argument.',
                ),
                z=z_doc,
            ),
            init=FuncDocstring(
                '__init__',
                FunctionType,
                args=OrderedDict(
                    name=name_doc,
                    a=docstring.ArgDoc(
                        'a',
                        int_float,
                        'Foo is an excellently documented string argument.',
                    ),
                    b=docstring.ArgDoc(
                        'b',
                        int_float,
                        'Foo is an excellently documented string argument.',
                    ),
                    x=docstring.ArgDoc(
                        'x',
                        int_float,
                        'Foo is an excellently documented string argument.',
                    ),
                    y=docstring.ArgDoc(
                        'y',
                        int_float,
                        'Foo is an excellently documented string argument.',
                    ),
                    z=z_doc,
                ),
            ),
            # TODO default ignore?, ignore properties, allow skip_missing_doc
            methods=dict(
                foo=FuncDocstring(
                    'foo',
                    FunctionType,
                    """The foo function performs Tom foo-ery. Heh heh.
                    However the long description of `foo()` is longer than the short
                    description but still not too long to be cumbersome.

                    Perhaps it can be too long and that's alright because it is the long
                    description. The long description can be as long as it wants or as
                    short as it wants; even non-existent.
                    """,
                    args=OrderedDict(
                        oh=docstring.ArgDoc(
                            'oh',
                            str,
                            'First word in the paired concatenation of string inputs.',
                        ),
                        my=docstring.ArgDoc(
                            'my',
                            str,
                            'Second word in the paired concatenation of string inputs.',
                        ),
                    ),
                    return_doc=docstring.BaseDoc(
                        'Returns',
                        str,
                        'Concatenate `oh` and `my` in that order.',
                    ),
                ),
            ),
        )

        # Decide if parser is function or class object.
        parsed = parse(examples.NumpyDocClass)

        # Comparison supported betweend the docstr.docstring classes.
        assert expected == parsed


    def test_class_doc_linking():
        # TODO use the given pre-made hook expected item.
        # TODO Create the expected result of docstring.

        # Decide if parser is function or class object.
        parsed = parse(examples.NumpyDocClassLinking)

        # Comparison supported betweend the docstr.docstring classes.
        assert expected == parsed


    def test_class_doc_2hop_linking_and_non_primitive_arg():
        # TODO Create the expected result of docstring.

        # Decide if parser is function or class object.
        parsed = parse(examples.NumpyDocClassMultiLinking)

        # Comparison supported betweend the docstr.docstring classes.
        assert expected == parsed