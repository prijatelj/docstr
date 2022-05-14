"""Object oriented design of tokenized representation of docstrings.
After parsing the docstrings, the result are these token objects filled out.
From these tokens, syntax checking as well as "compile" actions may occur.
"""
from enum import Flag, unique
from collections import OrderedDict
from dataclasses import dataclass, InitVar
import inspect
from keyword import iskeyword
import logging
from types import FunctionType
from typing import FrozenSet, Iterable
ClassType = type

import configargparse as cap

# Modify `sphinxcontrib.napoleon` to include `exputils` mod to Numpy style
# Use respective style: `sphinxcontrib.napoleon.GoogleDocstring(docstring,
# config)` to convert the docstring into ReStructuredText.
# Parse that restructured text to obtain the args, arg types, decsriptions,
# etc.

# TODO, I need the first working version of this done and while it seems like
# it would make the most sense to use and/or modify the sphinx DocTree of
# classes and functions to manage the OOP of docstrings, the sphinx docs and
# code upon my 3 attempts at reading and understanding did not yeild a
# sufficient enough understanding to be able to implement this probably more
# desirable approach. I think, if it is posisble to use the sphinx DocTree of
# classes and functions within the code itself, it would be best to rely on
# this pre-existing backbone and avoid redundancy.

# TODO, uncertain if this already exists, e.g. in Sphinx, but would be nice if
# we could go from the OOP representation of a docstring to the actual str
# easily, and swap styles. Probably similar to how Google and Numpy docs are
# parsed, where they are converted to reStructuredText and then parsed. So,
# output Docstring Object to str of RST and then optionally convert to Google
# or Numpy.

# TODO note that Factories or module level function that load classes need
# handeld by parsing their docstrings... when automating the loading of
# classes. Just keep it in mind, and note that Factories make sense when the
# sub classes, say a bunch of different torch.modules or tf.keras.models
#   naive solution is the factory has a docstr so give it to docstr to parse.

# TODO Go from these tokens to a "compiled" object.

def get_full_qual_name(obj):
    """Returns the given object's fully qualified name as a str."""
    return f'{obj.__module__}.{obj.__qualname__}'


@unique
class ValueExists(Flag):
    """Enum for standing in for a non-existent default value."""
    true = True
    false = False


# NOTE may use typing.Literal for this? Intended for checking return types, but
# perhaps this as well in cases where literal instances are expected?
"""A set of multiple types for when a variable may take multiple types."""
"""
@dataclass(frozen=True)
class MultiType:
    types : frozenset

    # TODO handle some internal assessment property that notes if this is a
    # multi type of all literals, if so, then it specifies the choices values
    # of that this variable may take.

    # TODO perhaps should preserve order of types? Otherwise need way to tell
    # which arbitrary type to cast to given some pattern hint in the input
    # string, or given some setting in another variable, either order of
    # priority, or pattern condition. Insertion ordered frozen/immutable set.

    # TODO isinstance(instance, multi_type_instance) ; or otherwise an
    # equivalent method, especialy since MultiType.isinstance() would keep it
    # clear this is about being in one of the multiple types, but
    # isinstance(instance, {'set', 'of', 'types'}) is desirable.
"""

class MultiType(tuple):
    """A frozenset of multipe types. As a callable, casts the objects into one
    of its types.
    """
    #def __new__(cls, types: Iterable):
    #    return super(MultiType, cls).__new__(cls, types)

    def check(self, objs):
        raise NotImplementedError('Consider pydantic? or extend argparse')
        # TODO for this to be worth an object, type checking/handling needs
        # implemented, but tbh, perhaps this does not to be an object anyways
        # due to stores tuple and would implement a single method that would
        # take object and tuple types?

    def __call__(self, x):
        if str in self: # prioritize str, mainly for when both str & list exist
            if isinstance(x, str):
                return x
        for cast_type in self:
            try:
                return cast_type(x)
            #except ValueError as err:
            except TypeError as err:
                if cast_type == x:
                    return cast_type
            except ValueError as err:
                pass
        raise ValueError(' '.join([
            f'The given object `{x}` is not cast-able to any of the types:'
            f'{self}'
        ]))



# TODO For each of these dataclasses, make them tokenizers for their respective
# parts of the docstring and string call them during parsing
@dataclass
class BaseDoc:
    """Dataclass for the base components of every parsed docstring object."""
    name : str = ValueExists.false
    type : type = ValueExists.false
    description : str = ValueExists.false


@dataclass
class ArgDoc(BaseDoc):
    """Dataclass for an argument/parameter in docstrings."""
    default : InitVar[object] = ValueExists.false

    def __post_init__(self, default):
        # Check if a valid name identifier for parameter (variable)
        if not self.name.isidentifier() or iskeyword(self.name):
            raise ValueError(
                f'`name` is an invalid parameter name: `{self.name}`'
            )
        self.default = default

    def update_parser(self, parser, prefix=None):
        # TODO I predict the prefix will be necessary to make a hierarch parser
        #   Unless, the parser object handles this itself, which I will
        #   probably have to make it do to keep the code clean and to be able
        #   to parse YAML with ConfigArgParse.

        # TODO need to handle lists, array likes, etc... (note append for
        # config parse), so then maybe not `nargs=+`?
        parser.add_argument(
            f'--{self.name}',
            default=None if self.default is ValueExists.false else self.default,
            # TODO choices= informed by type in numpy being a set of things.
            # The type is then informed by the set's elements, if not provided.
            help=self.description,
            # TODO Probably need a handler for some common objects?
            type=str if self.type is ValueExists.false else self.type,
            dest=f'{prefix}.{self.name}' if prefix else f'{self.name}',
        )

        # TODO need to handle `required` args, when they are positional args w/
        # no defaults, which means their value must be given.

        # TODO will probably have to handle certain action classes based on
        # type, defaults, and choices. e.g. Boolean only options w/ defaults.

        # TODO handle multi_typed_args (default type becomes a param here.)
        #   TODO perhaps in this case allow the user to specify the type of the
        #   parsed arg, if not apparent.

        # TODO check arg value to check arg dependencies on the value of other
        # args.

@dataclass
class Docstring:
    """The docstring components of a fully parsed `__doc__`."""
    type : object = ValueExists.false
    description : str = ValueExists.false
    # TODO ??? other_sections: OrderedDict({str : str}) = None

    # NOTE could swap type for obj and make properties type and name?

    @property
    def name(self):
        if self.type == ValueExists.false:
            raise ValueError('`type` was not assigned yet. Unable to get name')
        return self.type.__name__

    @property
    def full_qual_name(self):
        if self.type == ValueExists.false:
            raise ValueError('`type` was not assigned yet. Unable to get name')
        return get_full_qual_name(self.type)

    @property
    def short_description(self):
        if self.description == ValueExists.false:
            raise ValueError('`description` was not assigned yet.')
        return self.description.partition('\n')[0]


@dataclass
class FuncDocstring(Docstring):
    """The docstring components of a fully parsed function's `__doc__`.

    Attributes
    ----------
    args : str
        The function's Arguments/Args or the class' Attributes.
    """
    type : InitVar[object] = ValueExists.false
    args : OrderedDict({str : ArgDoc}) = None
    returns : BaseDoc = ValueExists.false

    def __post_init__(self, type):
        if not inspect.isroutine(type):
            raise TypeError(
                f"FuncDocstring given a type that's not a routine: {type}"
            )
        self.type = type

    def get_str(self, style):
        """Returns the docstring as a string in the given style. Could simply
        be __str__() and always return RST, and make available RST to
        Google/Numpy functions/classes.

        Args
        ----
        style : {'rst', 'google', 'numpy'}
            The style to output the Docstring's contents. `rst` is shorthand
            for reStructuredText.

        Returns
        -------
        str
            The contents of the Docstring instance as a string in the style.
        """
        raise NotImplementedError()


@dataclass
class ClassDocstring(Docstring):
    """The docstring components of a fully parsed class's `__doc__`.
    This consists of multiple `Docstrings` that make up a class, including at
    least the class' docstring and the __init__ method's docstring.
    """
    type : InitVar[object] = ValueExists.false
    attributes : OrderedDict({str : ArgDoc}) = None
    init : FuncDocstring = None
    methods : {str: FuncDocstring} = None

    def __post_init__(self, type):
        # TODO attributes are unnecessary for bare min config. uses init or
        # load-like function, but is useful for type checking.

        if not isinstance(type, ClassType):
            raise TypeError(
                f"ClassDocstring given a type that's not `type`: {type}"
            )
        self.type = type

        # NOTE rm this check as NestedTuple classes have no init w/ own __doc__
        #if init is None:
        #    raise TypeError(' '.join([
        #        'ClassDocstring() missing 1 required positional argument:',
        #        '`init_docstring` Provide via keyword, if unable to through',
        #        'position.',
        #    ]))
        #self.init = init


# TODO consider making a namespace object that is the root of Docstr's parsed
# tokens and allows for easy querying of namespace paths within it.
class Namespace(object):
    """Docstr's internal namespace representation object."""
    def __init__(self):
        pass
