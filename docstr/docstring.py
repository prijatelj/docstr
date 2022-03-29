"""Object oriented design of tokenized representation of docstrings.
After parsing the docstrings, the result are these token objects filled out.
From these tokens, syntax checking as well as "compile" actions may occur.
"""
from enum import Flag, unique
from collections import OrderedDict
from collections.abc import Set # MutableSet
from dataclasses import dataclass, InitVar
from keyword import iskeyword

import configargparse

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

@unique
class ValueExists(Flag):
    """Enum for standing in for a non-existent default value."""
    true = True
    false = False


#class MultiType(MutableSet):
# NOTE may use typing.Literal for this? Intended for checking return types, but
# perhaps this as well in cases where literal instances are expected?
@dataclass
class MultiType:
    """A list of multiple types for when a variable may take multiple types."""
    types : set

    # TODO handle some internal assessment property that notes if this is a
    # multi type of all literals, if so, then it specifies the choices values
    # of that this variable may take.

    def check(self, objs):
        raise NotImplementedError('Consider pydantic? or extend argparse')
        # TODO for this to be worth an object, type checking/handling needs
        # implemented, but tbh, perhaps this does not to be an object anyways
        # due to stores tuple and would implement a single method that would
        # take object and tuple types?


# TODO For each of these dataclasses, make them tokenizers for their respective
# parts of the docstring and string call them during parsing
@dataclass
class BaseDoc:
    """Dataclass for the base components of every parsed docstring object."""
    name : str
    type : type = ValueExists.false
    description : str = ValueExists.false


@dataclass
class ArgDoc(BaseDoc):
    """Dataclass for an argument/parameter in docstrings."""
    default : InitVar[object] = ValueExists.false
    #choices : object = ValueExists.false

    def __post_init__(self, default):
        # Check if a valid name identifier for parameter (variable)
        if not self.name.isidentifier() or iskeyword(self.name):
            raise ValueError(
                f'`name` is an invalid parameter name: `{self.name}`'
            )

        # TODO generalize this by extending InitVar to perform this in init.
        # Default the "empty" value to None, possibly removing need to specify
        # `= None` in the dataclass part. Just to expedite this cuz it is now
        # repeated in this code, which itself is meant to expedite through
        # write once... Probably would not inherity from InitVar, but do
        # something similar-ish. Moreso generate the code snippet in the
        # generated __init__(). could possibly even reorder positional args
        # based on the order of inheritance.
        if default is None: # TODO Wait what is wrong here???
            raise TypeError(' '.join([
                'ArgDoc() missing 1 required positional argument:',
                '`default` Provide via keyword, if able to through position.',
            ]))
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
class Docstring(BaseDoc):
    """The docstring components of a fully parsed `__doc__`.

    Attributes
    ----------
    args : str
        The function's Arguments/Args or the class' Attributes.
    """
    #short_description : InitVar[str] = None
    other_sections: OrderedDict({str : str}) = None

    @property
    def short_description(self):
        return self.description.partition('\n')[0]


@dataclass
class FuncDocstring(Docstring):
    """The docstring components of a fully parsed function's `__doc__`.

    Attributes
    ----------
    args : str
        The function's Arguments/Args or the class' Attributes.
    """
    args : OrderedDict({str : ArgDoc}) = None
    # TODO implement parsing. While some styles allow other args, whynot
    # combine in this token?
    #other_args : OrderedDict({str : ArgDoc}) = None
    returns : BaseDoc = ValueExists.false

    #def __post_init__(self, args):
    #    if args is None:
    #        raise TypeError(' '.join([
    #            'FuncDocstring() missing 1 required positional argument:',
    #            '`args` Provide via keyword, if able to through position.',
    #        ]))
    #    self.args  = args

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

    def get_parser(self, parser=None):
        if parser is None:
            parser = configargparse.ArgParser(
                prog=self.name,
                description=self.short_description,
            )
        else:
            parser = parser.add_argument_group(
                self.name,
                self.short_description,
            )

        for arg in self.args:
            arg.add_to_parser
            parser.add_agument(
                f'--'
            )

        return parser


@dataclass
class ClassDocstring(Docstring):
    """The docstring components of a fully parsed class's `__doc__`.
    This consists of multiple `Docstrings` that make up a class, including at
    least the class' docstring and the __init__ method's docstring.
    """
    attributes : OrderedDict({str : ArgDoc}) = None
    init : InitVar[FuncDocstring] = None
    methods : {str: FuncDocstring} = None

    def __post_init__(self, init):
        # TODO attributes are unnecessary for bare min config. uses init or
        # load-like function, but is useful for type checking.

        if init is None:
            raise TypeError(' '.join([
                'ClassDocstring() missing 1 required positional argument:',
                '`init_docstring` Provide via keyword, if unable to through',
                'position.',
            ]))
        self.init = init

    def get_parser(self, parser=None):
        """Creates the argparser from the contents of the ClassDocstring."""
        # TODO set args from __init__
        if parser is None:
            parser = configargparse.ArgParser(
                prog=self.name,
                description=self.short_description,
            )
        else:
            parser = parser.add_argument_group(
                self.name,
                self.short_description,
            )

        init_parser = self.init_docstring.get_parser(parser)


        # TODO set name, description

        # TODO set args from __init__

        return parser

# TODO consider making a namespace object that is the root of Docstr's parsed
# tokens and allows for easy querying of namespace paths within it.
class Namespace(object):
    """Docstr's internal namespace representation object."""
    def __init__(self): pass
