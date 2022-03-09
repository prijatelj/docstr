"""Tests of the compiler-like checking of docstrings to ensure they parse
styles as they are expected and includes examples of out-of-style
docstrings.
"""
from collections import OrderedDict
from types import FunctionType

import pytest

from docstr import docstring, parse

import testing.numpy_example_docstrings as examples
from testing.parsing.test_parse_class_with_primitives import (
    TestParseClassLinking,
    expected_class_linking,
)


@pytest.fixture
def expected_class_multi_linking(expected_class_linking):
    expected_class_linking.attributes.update(
        custom_obj_instance=ArgDoc(
            'custom_obj_instance',
            examples.NumpyDocClass,
            """An example of recusrive linking without `see namespace` that allows for
        specifying a custom class as the type and then recursively parsing that
        object, if desired, to make a complete configargparser w/ hierarchical
        namespaces.

        This functionality is set in the function that walks the docstrings and
        generates the configargparser.""",
        ),
        just_for_me=docstring.ArgDoc('just_for_me', bool, default=True),
    )
    return docstring.ClassDocstring(
        examples.NumpyDocClassMultiLinkning.__name__,
        examples.NumpyDocClassMultiLinkning,
        """A Numpy example class that uses multiple docstring linking of depth 2
        links.

        An example of linking text from the long description of another docstring:
        DO QUOTING MARKDOWNFOR SPHINX:
            $see `NumpyDocLinkingClass`$

        An example of linking a subset of text from the long description of another
        docstring:
        DO QUOTING MARKDOWNFOR SPHINX:
            # TODO make this the Math LaTex and hyperlinking
            $see `NumpyDocClass`[3:5]$

        # TODO labeled/subsection linking to avoid using indexing of long
        # description by lines?""",
        attributes=expected_class_linking.attributes,
        init=None,
        methods=expected_class_linking.methods,
    )



class TestParseClassMultiLinking(TestParseClassLinking):
    @pytest.mark.dependency(
        name='TestParseClassMultiLinking',
        depends=['TestParseClassLinking'],
    )
    def test_class_doc_2hop_linking_and_non_primitive_arg(
        expected_class_multi_linking
    ):
        parsed = parse(examples.NumpyDocClassMultiLinking)
        assert expected_class_multi_linking == parsed
