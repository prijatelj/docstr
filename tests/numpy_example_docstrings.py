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
        name : see Attr
        a : int | float
            First number in summation.
        b : int | float
            Second number in summation.
        x : int | float = 8
            First number in multiplication.
        y : int | float defaults 11
            Second number in multiplication. This is an example of alternative
            specification of default. This support is included in order to be
            more inclusive of pre-existing standards used by others so that
            docstr could be applied to these cases. Docstr is intended to allow
            modifcation to their parsing regexes such that custom support for
            niche user cases may be handled by the user.
        z : see Attr
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


class NumpyDocClassMultiLinking(NumpyDocLinkingClass):
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
    see `NumpyDocClass`
    """
    def __init__(self, custom_obj_instance, just_for_me=True, *args, **kwargs):
        custom_obj_instance = self.custom_obj_instance
        self.just_for_me = just_for_me
        super(self, NumpyDocLinkingClass).__init__(*args, **kwargs)


# TODO dataclass example (Splat Extention is the dataclass example)
# TODO @docstr.meta.splat_extention(type_checking=True)
class NumpyDocClassSplatExtention(NumpyDocClassRecursiveLinking):
    """A Numpy example class that uses docstr's Splat Extention.
    Splat Extension reduces redundant coding by allowing the programmer to
    write the params only in the docstring while leaving the params in the
    function definition as `function(*args, **kwargs)`. Docstr is designed to
    remove redundant coding by relying on proper docstrings, and splat
    extention takes that further through meta-programming.

    Using `docstr.splat_extention` requires a docstr decorator, otherwise the
    class would not be operable because all the params in the docstring are
    expected to be extended into their respective namespace from the `*args`
    and `**kwargs`.

    Splat Extention extends dataclasses such that there is no need to specify
    the attribute assignment in the `__init__`. Default values are supported.
    Like dataclasses (SUBJECT TO CHANGE), this reilies on a `__post_init__()`
    to do any specific things to args after automated initialization.

    TODO: The decorator makes it so that this class (or function if used on a
    function) is masked such that when accessed or instantiated, it is treated
    as if the class was written as normally with all the parts existing as if
    normal.

    Also this is parsed once, such that the generated class is never re-parsed
    inefficiently.

    When type checking is True, then the code that is typically manually
    written to either assert or check and throw type errors is automatically
    generated in `__init__`. If a carry through option is specified, i.e. the
    decorator above affects all methods within the class, then it is necessary
    to include decorators that allow for specifying if that method has type
    checking or not to differ from the specified default from the class
    decorator used.

    Attributes
    ----------
    op_name : str
        The name of the operation.
    end_of_redundancy : True
        Note that this is implying type boolean when specifying a value of
        `True`.
    $see `NumpyDocClassRecursiveLinking`$

    Notes
    -----
    Note that this test example depends on the pass of docstring linking tests
    for examplifying concise docstring writing and to show how it works with
    linking.

    References
    ----------
    Some cited references for that proper citation like a good scientist.
    """
    #def __init__(self, *args, **kwargs):
    #   Unnecessary?

    # TODO Do the splats even need written in post init?
    # TODO How would you use *args and **splat as normal if so?
    #   Answer: rm all attribs/args from it and then use as normal.
    def __post_init__(self, *args, **kwargs):
        """Post init is the same as in dataclasses. It is used when specific
        things for this class need done beyond the simple saving of specific
        args w/ defaults, otherwise it is unnecessary.

        Args
        ----
        class_specific_value_1 : int | float
            This is analogous to dataclass Init only parameters, but are
            naturally specified as such as being included as args in the
            docstrings without values in the attributes. Furthermore,
            attributes are already saved and used as expected in dataclass
            automated __init__, so in __post_init__ they are accessed through
            `self.attribute`
        class_specific_value_2 : int | float
            $see
            `NumpyDocClassSplatExtention.__post_init__.class_specific_value_1`$
        operation: `lambda v1, v2: v1 + v2`
            Note that this case allows removing the type specificaiton as that
            is implied by the object itself (SUBJECT TO CHANGE).

            SUBJECT TO CHANGE note means that this functionality is not
            determined for certain yet, but it seems like it may be beneficial.
            Also this paragraph is an example of a multi paragraph description
            of an attribute. This only works for python primitives, but it may
            be possible to specify that it is an instance using backtics.
            Currently, I am uncertain if the backtics are necessary for python
            lambda functions.
        """
        self.op_result = operation(
            class_specific_value_1,
            class_specific_value_2,
        )

    #@docstr.meta.splat_extention(type_checking=True) TODO necessary?
    def bar(self, *args, **kwargs):
        """Method overrides parent and the params are expanded by docstr.meta

        Args
        ----
        players : int
        blitzball : bool = False

        Returns
        -------
        bool
            The games' result, whether not blitzball (default) or blitzball.
            True is a win, False is a loss.
        """
        return blitzball or players > 1
