"""A Numpy docstring example. This is used to test conversions and parsing."""
# TODO make Numpy and Google exhaustive examples that get converted


def numpy_doc_func(foo, bar):
    """This is the short desc. of the function, concat the paired strings

    Args
    ----
    foo : str
        Foo is an excellently documented string argument.
    bar : str
        Bar is an excellently documented string argument.

    Returns
    -------
    str
        An incredible ordered concatenation of the paired string inputs.
    """
    return foo + bar


def numpy_doc_func_defaults(foo='foo', bar='bar'):
    """This is the short desc. of the function, concat the paired strings

    Args
    ----
    foo : str = 'foo'
        Foo is an excellently documented string argument.
    bar : str = 'bar'
        Bar is an excellently documented string argument.

    Returns
    -------
    str
        An incredible ordered concatenation of the paired string inputs.
    """
    return foo + bar


def numpy_doc_func_choices(foo='foo', bar='bar'):
    """This is the short desc. of the function, concat the paired strings

    Args
    ----
    foo : 'foo' | 'bar' = 'foo'
        Foo is an excellently documented string argument.
    bar : 'foo' | 'bar' = 'bar'
        Bar is an excellently documented string argument.

    Returns
    -------
    str
        An incredible ordered concatenation of the paired string inputs.
    """
    return foo + bar


def numpy_doc_func_alt_defaults(foo='foo', bar='bar'):
    """This is the short desc. of the function, concat the paired strings

    Args
    ----
    foo : str defaults 'foo'
        Foo is an excellently documented string argument.
    bar : str, optional
        Bar is an excellently documented string argument.

    Returns
    -------
    str
        An incredible ordered concatenation of the paired string inputs.
    """
    # TODO eval on alternate defaults
    # TODO eval on having to infer from code the default.
    return foo + bar


def numpy_doc_func_linking(foo='foo', bar='bar'):
    """This is the short desc. of the function, concat the paired strings

    Args
    ----
    see numpy_doc_func_defaults

    Returns
    -------
    str
        An incredible ordered concatenation of the paired string inputs.
    """
    return foo + bar


def numpy_doc_func_linking_arg_pass_thru(foo, bar='bar'):
    """This is the short desc. of the function, concat the paired strings

    Args
    ----
    foo : see numpy_doc_func_defaults
    bar : see numpy_doc_func_choices

    Returns
    -------
    str
        An incredible ordered concatenation of the paired string inputs.
    """
    return foo + bar


def numpy_doc_func_linking_args(boo='foo', far='bar'):
    """This is the short desc. of the function, concat the paired strings

    Args
    ----
    boo : see numpy_doc_func_defaults.foo
    far : see numpy_doc_func_choices.bar

    Returns
    -------
    str
        An incredible ordered concatenation of the paired string inputs.
    """
    return boo + far


def numpy_doc_func_linking_see_end(fizz, buzz, foo='foo', bar='bar'):
    """This is the short desc. of the function, concat the paired strings

    Args
    ----
    fizz: str
        An excellently documented string argument.
    buzz: 'fizz' | 'buzz'
        An excellently documented string argument.
    see numpy_doc_func_defaults

    Returns
    -------
    str
        An incredible ordered concatenation of the ordered string inputs.
    """
    return fizz + buzz + foo + bar

def numpy_doc_func_linking_see_start(
    foo='foo',
    bar='bar',
    fizz='fizz',
    buzz='buzz',
):
    """This is the short desc. of the function, concat the paired strings

    Args
    ----
    see numpy_doc_func_defaults
    fizz: str = 'fizz'
        An excellently documented string argument.
    buzz: 'fizz' | 'buzz' = 'buzz'
        An excellently documented string argument.

    Returns
    -------
    str
        An incredible ordered concatenation of the ordered string inputs.
    """
    return foo + bar + fizz + buzz


def numpy_doc_func_linking_see_mid(
    fizz,
    foo='foo',
    bar='bar',
    buzz='buzz',
):
    """This is the short desc. of the function, concat the paired strings

    Args
    ----
    fizz: str
        An excellently documented string argument.
    see numpy_doc_func_defaults
    buzz: 'fizz' | 'buzz' = 'buzz'
        An excellently documented string argument.

    Returns
    -------
    str
        An incredible ordered concatenation of the ordered string inputs.
    """
    return fizz + foo + bar + buzz


def numpy_doc_func_linking_local(foo='foo', bar='foo'):
    """Doc linking to an arg within the local context, another arg.

    Args
    ----
    foo : str = 'foo'
        An excellently documented string argument.
    bar : see foo

    Returns
    -------
    str
        An incredible ordered concatenation of the ordered string inputs.
    """
    return foo + bar


def numpy_doc_func_linking_1hop(foo='foo', bar='foo'):
    """Doc linking with 1 recursive hop, where a local see occurs.

    Args
    ----
    see numpy_doc_func_linking_local

    Returns
    -------
    str
        An incredible ordered concatenation of the ordered string inputs.
    """
    return foo + bar


def numpy_doc_func_linking_2hop(foo='foo', bar='foo'):
    """Doc linking with 2 recursive hops, where a local see occurs at the end.

    Args
    ----
    see numpy_doc_func_linking_1hop

    Returns
    -------
    str
        An incredible ordered concatenation of the ordered string inputs.
    """
    return foo + bar


class NumpyDocClass(object):
    """This is an example class with Numpy docstrings. Short description ends.
    This is the beginning of the long descriptions, which can essentially be
    arbitrary text until the next section/field occurs.

    # TODO include MathTex/LaTeX math here to ensure parsing works with it.
    I don't think I can use the `$` character to delimit docstr linking as
    MathTex may use it! So I need to ensure the character I use is commonly NOT
    used by other things wrt docstrings. Perhaps I could just use the markdown
    for hyperlinking, but use some indication of namespace / within code
    linking.

    # TODO Include example of hyperlinking in long description

    Attributes
    ----------
    name : str
        The name associated with the object instance.
    a_plus_b : int | float
        The addition of two given numbers upon initialization. This also
        includes the allowance of two types of `int` and `float`.
    x_times_y : float
        The multiplication of two given numbers upon initialization.

        # TODO include markdown for LaTeX Math here as a test case of parsing.
    c : int | float
        Given number upon initialization that may be either an int or a float.
    z : float = 3.14159
        An example of an attribute with a default value, typically set in init.
    """
    def __init__(self, name, a, b, c, x=8, y=11, z=3.14159):
        """
        Args
        ----
        name : see self
        a : int | float
            First number in summation.
        b : int | float
            Second number in summation.
        x : int | float = 8
            First number in multiplication.
        y : int | float = 11
            Second number in multiplication. This is an example of alternative
            specification of default. This support is included in order to be
            more inclusive of pre-existing standards used by others so that
            docstr could be applied to these cases. Docstr is intended to allow
            modifcation to their parsing regexes such that custom support for
            niche user cases may be handled by the user.
        z : see self
        """
        self.name = name
        self.a_plus_b = a + b
        self.x_times_b = float(x * y)
        self.c = c
        self.z = float(z)

    def foo(self, oh, my):
        """The foo function performs Tom foo-ery. Heh heh.
        However the long description of `foo()` is longer than the short
        description but still not too long to be cumbersome.

        Perhaps it can be too long and that's alright because it is the long
        description. The long description can be as long as it wants or as
        short as it wants; even non-existent.

        Args
        ----
        oh : str
            First word in the paired concatenation of string inputs.
        my : str
            Second word in the paired concatenation of string inputs.

        Returns
        -------
        str
            Concatenate `oh` and `my` in that order.
        """
        return oh + my


class NumpyDocClassLinking(NumpyDocClass):
    """A Numpy example class that uses docstring linking.

    Attributes
    ----------
    example_var : object
    is_this_correct : bool = False

    Other Attributes
    ----------------
    see `NumpyDocClass`
        Allow for 1) a section of text under docstring linking of 'see', This
        is discarded in the parsed tokens 2) for docstrings of classes w/
        inheritance to not have to specify `see`. The latter being a parsing
        option that will check the parent(s) docstrings for any missing
        attributes that should persist in this child class.
    """
    def __init__(self, example_var, is_this_correct=False, *args, **kwargs):
        super(self).__init__(*args, **kwargs)

        # NO docstring, still fine to support, perhaps docstr logs a warning.
        self.example_var = example_var
        self.is_this_correct = is_this_correct

    def bar(self, oh, my):
        """Same args as foo, but performs a different operation.

        Args
        ----
        see `NumpyDocClass.foo`
            Other "Args" or Other "Attributes" is not necessary, but is
            supported. TODO `see `namespace`` can simply be set under the
            args/attributes section as done so here. Also this comment is
            optional and the parsing of such links may need handled such that
            Sphinx works well with them, i.e. auto-generates them or does the
            linking correctly.

        Returns
        -------
        str
            Concatenate `my` and `oh` in that order.
        """
        return my + oh


class NumpyDocClassMultiLinking(NumpyDocClassLinking):
    """A Numpy example class that uses multiple docstring linking of depth 2
    links.

    An example of linking text from the long description of another docstring:
    DO QUOTING MARKDOWNFOR SPHINX:
        $see `NumpyDocClassLinking`$

    An example of linking a subset of text from the long description of another
    docstring:
    DO QUOTING MARKDOWNFOR SPHINX:
        # TODO make this the Math LaTex and hyperlinking
        $see `NumpyDocClass`[3:5]$

    # TODO labeled/subsection linking to avoid using indexing of long
    # description by lines?

    Attributes
    ----------
    custom_obj_instance : NumpyDocClass
        An example of recusrive linking without `see namespace` that allows for
        specifying a custom class as the type and then recursively parsing that
        object, if desired, to make a complete configargparser w/ hierarchical
        namespaces.

        This functionality is set in the function that walks the docstrings and
        generates the configargparser.
    just_for_me : bool = True
    see `NumpyDocClassLinking`
    """
    def __init__(self, custom_obj_instance, just_for_me=True, *args, **kwargs):
        custom_obj_instance = self.custom_obj_instance
        self.just_for_me = just_for_me
        super(self, NumpyDocClassLinking).__init__(*args, **kwargs)
