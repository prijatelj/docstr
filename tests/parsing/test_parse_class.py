"""Tests of the compiler-like checking of docstrings to ensure they parse
styles as they are expected and includes examples of out-of-style docstrings.

TODO FixMe
----------
The docutils.parse_rst() removes useful things. Future fixme.

Backticks in document descriptions are not supported due to
docutils.parse_rst() removing them from the string when parsed. There may be
a configuration/setting option to avoid this, but funny enough, their
documentaiton is not clear enough for the time I was willing to put into
figuring that out.

Removes empty lines in long descriptions, etc. for whatever reason.

Docutils current implementation in docstr 0.1 requires Attributes to have an
empty line before it to be recognized in parsing the RST...
"""
from collections import OrderedDict
from collections.abc import Callable
from types import FunctionType

import pytest

from docstr import docstring, parse

import tests.numpy_example_docstrings as examples


@pytest.fixture
def expected_class_of_primitives():
    # NOTE the same object is used in both attr and args, this is desirable from
    # docstr linking.
    name_doc = docstring.ArgDoc(
        'name',
        str,
        'The name associated with the object instance.',
    )
    z_doc = docstring.ArgDoc(
        'z',
        float,
        'An example of an attribute with a default value, typically set in init.',
        3.14159,
    )
    ok_doc = docstring.ArgDoc(
        'ok',
        bool,
        """A bool attribute test for configargparse. There were issues before in
the prototype where any non-empty str input including "False" and
"True" were cast to True, whether in config or cli args.""",
        False,
    )
    # NOTE That here, int_float is shorthand, and the objects won't be the same
    # in the actual parsed docstring.
    int_float = docstring.MultiType((int, float))

    return docstring.ClassDocstring(
        examples.NumpyDocClass,
        """This is an example class with Numpy docstrings. Short description ends.
This is the beginning of the long descriptions, which can essentially be
arbitrary text until the next section/field occurs.
# TODO include MathTex/LaTeX math here to ensure parsing works with it.
I don't think I can use the $ character to delimit docstr linking as
MathTex may use it! So I need to ensure the character I use is commonly NOT
used by other things wrt docstrings. Perhaps I could just use the markdown
for hyperlinking, but use some indication of namespace / within code
linking.
# TODO Include example of hyperlinking in long description""",
        attributes=OrderedDict(
            name=name_doc,
            a_plus_b=docstring.ArgDoc(
                'a_plus_b',
                int_float,
                """The addition of two given numbers upon initialization. This also
includes the allowance of two types of int and float.""",
            ),
            x_times_y=docstring.ArgDoc(
                'x_times_y',
                float,
                """The multiplication of two given numbers upon initialization.
# TODO include markdown for LaTeX Math here as a test case of parsing.""",
            ),
            c=docstring.ArgDoc(
                'c',
                int,
                'Number set upon initialization that increments as foo is used.',
                0,
            ),
            z=z_doc,
            ok=ok_doc,
        ),
        init=docstring.FuncDocstring(
            examples.NumpyDocClass.__init__,
            args=OrderedDict(
                name=name_doc,
                a=docstring.ArgDoc(
                    'a',
                    int_float,
                    'First number in summation.',
                ),
                b=docstring.ArgDoc(
                    'b',
                    int_float,
                    'Second number in summation.',
                ),
                x=docstring.ArgDoc(
                    'x',
                    int_float,
                    'First number in multiplication.',
                    8,
                ),
                y=docstring.ArgDoc(
                    'y',
                    int_float,
                    """Second number in multiplication. This is an example of alternative
specification of default. This support is included in order to be
more inclusive of pre-existing standards used by others so that
docstr could be applied to these cases. Docstr is intended to allow
modifcation to their parsing regexes such that custom support for
niche user cases may be handled by the user.""",
                    11,
                ),
                z=z_doc,
                ok=ok_doc,
            ),
        ),
        # TODO default ignore?, ignore properties, allow skip_missing_doc
    )


@pytest.fixture
def expected_class_of_primitives_methods(expected_class_of_primitives):
    expected_class_of_primitives.methods=dict(
        foo=docstring.FuncDocstring(
            examples.NumpyDocClass.foo,
            """The foo function performs Tom foo-ery. Heh heh.
However the long description of foo() is longer than the short
description but still not too long to be cumbersome.
Perhaps it can be too long and that's alright because it is the long
description. The long description can be as long as it wants or as
short as it wants; even non-existent.""",
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
            returns=docstring.BaseDoc(
                'returns',
                str,
                'Concatenate oh and my in that order.',
            ),
        ),
    )
    return expected_class_of_primitives


@pytest.fixture
def expected_class_recursive_parse():
    args = OrderedDict(
        very_useful_class=docstring.ArgDoc(
            'very_useful_class',
            examples.NumpyDocClass,
            'Truly, a very useful class instance.',
        ),
        func_2=docstring.ArgDoc(
            'func_2',
            Callable,
            "A function to be called throughout the class' use.",
            examples.func_defaults,
        ),
    )
    return docstring.ClassDocstring(
        examples.NumpyDocClassRecursiveParse,
        'A class with objects to be parsed.',
        attributes=args,
        init=docstring.FuncDocstring(
            examples.NumpyDocClassRecursiveParse.__init__,
            """I have a description, unlike NumpyDocClass, but whatever really.
I also support see self shorthand for all attributes are args, as
expected of see namespace.path.to.object.""",
            args=args,
        ),
    )


@pytest.fixture
def expected_class_recursive_parse_whitelist(
    expected_class_of_primitives,
    expected_class_recursive_parse,
):
    expected_class_recursive_parse.attributes['very_useful_class'].type = \
        expected_class_of_primitives
    expected_class_recursive_parse.init.args['very_useful_class'].type = \
        expected_class_of_primitives
    return expected_class_recursive_parse


@pytest.fixture
def expected_class_recursive_parse_methods(expected_class_recursive_parse):
    # TODO, show how to handle the run() method, if even parsed.
    expected_class_recursive_parse.methods=dict(run='')
    return expected_class_recursive_parse


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
        bar=docstring.FuncDocstring(
            examples.NumpyDocClassLinking.bar,
            'Same args as foo, but performs a different operation.',
            args=expected_class_of_primitives.methods['foo'].args
        )
    )
    return docstring.ClassDocstring(
        examples.NumpyDocClassLinking,
        'A Numpy example class that uses docstring linking.',
        attributes=expected_class_of_primitives.attributes,
        init=None,
        methods=expected_class_of_primitives.methods,
    )


@pytest.fixture
def expected_class_multi_linking(expected_class_linking):
    expected_class_linking.attributes.update(
        custom_obj_instance=docstring.ArgDoc(
            'custom_obj_instance',
            examples.NumpyDocClass,
            """An example of recusrive linking without see namespace that allows for
specifying a custom class as the type and then recursively parsing that
object, if desired, to make a complete configargparser w/ hierarchical
namespaces.
This functionality is set in the function that walks the docstrings and
generates the configargparser.""",
        ),
        just_for_me=docstring.ArgDoc('just_for_me', bool, default=True),
    )
    return docstring.ClassDocstring(
        examples.NumpyDocClassMultiLinking,
        """A Numpy example class that uses multiple docstring linking of depth 2
links.
An example of linking text from the long description of another docstring:
DO QUOTING MARKDOWNFOR SPHINX:
    $see NumpyDocLinkingClass$
An example of linking a subset of text from the long description of another
docstring:
DO QUOTING MARKDOWNFOR SPHINX:
# TODO make this the Math LaTex and hyperlinking
    $see NumpyDocClass[3:5]$
# TODO labeled/subsection linking to avoid using indexing of long
# description by lines?""",
        attributes=expected_class_linking.attributes,
        init=None,
        methods=expected_class_linking.methods,
    )


"""
@pytest.mark.dependency(
    depends=['tests/parsing/test_parse_func.py::parse_defaults_choices'],
    #depends=['parse_defaults_choices'],
    scope='session',
)#"""
@pytest.mark.incremental
class TestParseClass:
    def test_class_of_primitives(self, expected_class_of_primitives):
        """Tests the example class of primitives, but also includes attribute
        as init arg inherent pass through, which only works when not using meta
        splat expansion.
        """
        parsed = parse(examples.NumpyDocClass, 'numpy')
        assert expected_class_of_primitives == parsed

    def test_class_recursive_parse(self, expected_class_recursive_parse):
        parsed = parse(examples.NumpyDocClassRecursiveParse, 'numpy')
        assert expected_class_recursive_parse == parsed

    def test_class_recursive_parse_whitelist(
        self,
        expected_class_recursive_parse_whitelist,
    ):
        parsed = parse(
            examples.NumpyDocClassRecursiveParse,
            'numpy',
            whitelist={'tests.numpy_example_docstrings.NumpyDocClass'},
        )
        assert expected_class_recursive_parse_whitelist == parsed

    @pytest.mark.xfail
    def test_class_doc_linking(self, expected_class_linking):
        parsed = parse(examples.NumpyDocClassLinking, 'numpy')
        assert expected_class_linking == parsed

    def test_class_doc_2hop_linking_and_non_primitive_arg(
        self,
        expected_class_multi_linking
    ):
        parsed = parse(examples.NumpyDocClassMultiLinking, 'numpy')
        assert expected_class_multi_linking == parsed
