"""A Numpy docstring example. This is used to test conversions and parsing."""
from .numpy_example_docstrings import NumpyDocClassMultiLinking


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
