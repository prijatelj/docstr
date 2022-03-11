"""Code for parsing docstrings."""
import builtins
from collections import OrderedDict
from copy import deepcopy
#from functools import wraps
from inspect import getmodule
from keyword import iskeyword
import re
from typing import NamedTuple
from types import FunctionType

import docutils
from docutils import nodes
from docutils.parsers import rst
from sphinx.ext.autodoc import getdoc, prepare_docstring
from sphinx.ext.napoleon import Config, GoogleDocstring, NumpyDocstring

from docstr.docstring import (
    ValueExists,
    MultiType,
    ArgDoc,
    ClassDocstring,
    FuncDocstring,
    BaseDoc,
)

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

# TODO optionally set how to handle long descriptions for argparse help.


def get_namespace_obj(namespace, name, default=ValueExists.false):
    """Given a str of an object's identifier in the given object whose module
    is used as the namespace, returns the object, otherwise returns the default
    if given or raises error."""
    try:
        return getattr(namespace, name)
    except AttributeError as e:
        if default != ValueExists.false:
            return default
        raise e


def get_builtin(name, default=ValueExists.false):
    """Accesses pythons builtins using a key as a dictionary access via get."""
    return get_namespace_obj(builtins, name, default)


def get_object(namespace_obj, name, default=ValueExists.false):
    """Given a str of an object's identifier in the given object whose module
    is used as the namespace, returns the object, otherwise returns the default
    if given or raises error. The name is first checked if it is a python
    builtin object, otherwise it will attempt to return the attribute of the
    same given `name` in the module that namespace_obj is contained within.
    If the namespace_obj is a module itself, then it will be used to get the
    attribute `name`.
    """
    try:
        return get_builtin(name, default)
    except AttributeError as e:
        return get_namespace_obj(getmodule(namespace_obj), name, default)
    # TODO handle being given an instance of an object, esp. primitive.


class AttributeName(nodes.TextElement):
    """Contains the text of the attribute type."""
    pass


class AttributeType(nodes.TextElement):
    """Contains the text of the attribute type."""
    pass


class AttributeBody(nodes.Structural, nodes.Element):
    """Contains the AttributeType and paragraph body of an attribute."""
    pass


class AttributeDirective(rst.Directive):
    """ReST parser for python class docstring attributes."""
    required_arguments = 1
    optional_arguments = 0
    has_content = True

    def run(self):
        # Raise an error if the directive does not have contents.
        self.assert_has_content()

        print(self.name)
        print(self.arguments)

        node = AttributeBody()
        name_node = AttributeName()
        name_node += nodes.Text(self.arguments[0])
        node += name_node

        # Use the type option to create its own node, removing from body.
        content = deepcopy(self.content)
        pop = None
        for i, line in enumerate(content):
            if ':type:' == line[:6]:
                type_node = AttributeType()
                type_node += nodes.Text(line[6:].strip())
                node += type_node
                pop = i
                break

        if pop is not None:
            del content[i]
        else:
            raise ValueError('No attribute type for {self.arguments[0]}!')

        # Parse the body content as paragraphs
        para = nodes.paragraph()
        self.state.nested_parse(content, self.content_offset, para)
        node += para

        return [node]


def parse_rst(text: str) -> nodes.document:
    """Parses given RST text into a docutils document."""
    parser = rst.Parser()
    settings = docutils.frontend.OptionParser(
        components=(rst.Parser,),
    ).get_default_values()
    document = docutils.utils.new_document('<rst-doc>', settings=settings)
    parser.parse(text, document)

    return document


def _obj_defaults(obj, name=None, obj_type=ValueExists.false):
    """Given the object and optionally its information, return the object's
    docstring, name, and object type.

    Args
    ----
    obj : object | str
        The object whose __doc__ is to be parsed. If a str object of the
        docstring, then the `name` and `obj_type` parameters must be
        provided.
    name : str, optional
        The name of the object whose docstring is being parsed. Only needs
        to be supplied when the `obj` is a `str` of the docstring to be
        parsed, otherwies not used.
    obj_type : type, optional
        The type of the object whose docstring is being parsed. Only needs
        to be supplied when the `obj` is a `str` of the docstring to be
        parsed, otherwies not used.

    Returns
    -------
    (str, str, type)
        A tuple of docstring, object name, and object type.
    """
    # TODO separate this explicit giving from the automated finding check
    #   The explicit giving of names etc is weird and probs unnecessary.
    if isinstance(obj, str):
        if name is None:
            raise ValueError('`fname` must be given if `obj` is a `str`.')
        if obj_type is ValueExists.false:
            raise ValueError(
                '`obj_type` must be given if `obj` is a `str`.'
            )
        docstring = obj
    else:
        docstring =  obj.__doc__
        if docstring is None:
            raise ValueError(
                'The docstring of object `{obj}` does not exist.'
            )
        if name is None:
            name =  obj.__name__
        if obj_type is ValueExists.false:
            obj_type =  type(obj)

    return docstring, name, obj_type


class DocstringParser(object):
    """Docstring parser for a specific style and parser config.

    Attributes
    ----------
    style : {'rst', 'numpy', 'google'}
        The style expected to parse.
    doc_linking : bool = False
    config : sphinx.ext.napoleon.Config = None
    """
    def __init__(self, style, doc_linking=False, config=None):
        """
        Args
        ----
        style : 'numpy' | 'google' | 'rest' | str
            The docstring style to expect when parsing. Default choices are
            {'numpy', 'google', 'rest'}, although any string may be given as
            long as there is a sphinx style conversion extention available.
        doc_linking : bool = False
            Not Implemented Yet
        config : sphinx.ext.napoleon.Config = None
            Not Implemented Yet
        """
        style = style.lower()
        if style not in {'rst', 'numpy', 'google'}:
            raise ValueError(
                "Expected `style` = 'rst', 'numpy', or 'google', not `{style}`"
            )
        # TODO allow the passing of a func/callable to transform custom doc
        # styles, thus allowing users to easily adapt to their doc style
        self.style = style
        self.doc_linking = doc_linking

        if config is None:
            self.config = Config(
                napoleon_use_param=True,
                napoleon_use_rtype=True,
            )
        else:
            self.config = config

        # TODO section tokenizer (then be able to tell if the section is one of
        #   param/arg or type and to pair those together.
        #   attribute sections `.. attribute:: attribute_name`

        # Regexes for RST field and directive, and together for sections
        self.re_field = re.compile(r':[ \t]*(\w[ \t]*)+:')
        self.re_directive = re.compile(r'\.\.[ \t]*(\w[ \t]*)+:')
        self.re_section = re.compile(
            '|'.join([self.re_field.pattern, self.re_directive.pattern])
        )

        # Temporary useful patterns to build others from
        section_end_pattern = fr'{self.re_section.pattern}|\Z'
        name_pattern = r'[ \t]+(?P<name>[\*\w]+)'
        # Non-Greedy kleene star
        doc_pattern = fr'[ \t]*(?P<doc>.*?)({section_end_pattern})'

        # Regexes for checking and parsing the types of sections
        self.re_param = re.compile(fr'param{name_pattern}')
        #self.re_type = re.compile(fr':type{name_pattern}:{doc_pattern}', re.S)
        # docutils splits name and doc pattern into field name and field body
        self.re_type = re.compile(fr'type{name_pattern}')

        # For parsing the inner parts of a parameter type string.
        # Captures the type or multi-types as a list
        #self.re_default = re.compile(
        #    r'(?<=|,[ \t]*default)[ \t]*(?P<default>[^\s]+)'
        #)
        # Must be applied after default match is removed
        #self.re_typedoc = re.compile(r'(?:[ \t]*\|[ \t]*)*(\s+)')
        self.re_typedoc = re.compile(''.join([
            r'[ \t]*(?:\|[ \t]*)*',
            r'(?P<name>[^\s|]+)',
            r'(?:[ \t]*=[ \t]*',
            r'(?P<default>[^\s|]+))?',
        ]))

        self.re_returns = re.compile(':returns:{doc_pattern}', re.S)
        self.re_rtype = re.compile(':rtype:{doc_pattern}', re.S)

        self.re_attribute = re.compile(
            fr'\.\.[ \t]*attribute[ \t]*::{name_pattern}[ \t]*\n{doc_pattern}',
            re.S,
        )
        # TODO extract attribute type ':type: <value>\n'
        #   Need to fix doc pattern here... this is wrong.
        self.re_attr_type = re.compile(fr'[ \t]+:type:{doc_pattern}', re.S)

        self.re_rubric = re.compile(
            fr'\.\.[ \t]*attribute[ \t]*::{name_pattern}[ \t]*\n{doc_pattern}',
            re.S,
        )

        # Register AttributeDirective once for this parser.
        rst.directives.register_directive('attribute', AttributeDirective)

    def _parse_initial(self, docstring):
        """Internal util for pasring inital portion of docstring."""
        docstring = prepare_docstring(docstring)

        # NOTE for now, use what is specified at initialization
        #style = self.style if style is None else style.lower()
        #doc_linking = self.doc_linking if doc_linking is None else doc_linking

        # Convert the docstring is in reStructuredText styling
        if self.style == 'google':
            docstring = GoogleDocstring(docstring, self.config).lines()
        elif self.style == 'numpy':
            docstring = NumpyDocstring(docstring, self.config).lines()
        # TODO allow the passing of a func/callable to transform custom doc
        # styles

        # TODO parse the RST docstring
        #   TODO find Args/Args and other Param like sections.
        #   TODO Get all param names, their types (default to object w/ logging
        #   of no set type), and their descriptions

        #if len(docstring) < 1:
        #    raise ValueError('The docstring is only a short description!')

        return '\n'.join(docstring)

    def parse_func(self, obj, fname=None):
        """Parse the docstring of a function.

        Args
        ----
        obj : object | str
            The object whose __doc__ is to be parsed.
        fname : str, optional
            The name of the object whose docstring is being parsed. Only needs
            to be supplied when the `obj` is a `str` of the docstring to be
            parsed, otherwies not used.
        """
        docstring = self._parse_initial(obj.__doc__)
        # Use docutils to parse the RST (one pass... followed by more.)
        doc = parse_rst(docstring)

        if description := doc.first_child_not_matching_class(nodes.paragraph):
            description = '\n'.join(
                [ch.astext() for ch in doc.children[:description]]
            )

        if not (field_list := doc.first_child_matching_class(
            nodes.field_list
        )):
            raise ValueError('The given docstring includes no fields!')

        # The field list includes params, types, returns, and rtypes,
        field_list = doc.children[field_list]

        # Prepare the paired dicts for params to catch dups, & missing pairs
        params = OrderedDict()
        types = OrderedDict()
        returns = ValueExists.false
        # Go through the field_list and parse the values.
        for field in field_list:
            field_name = field.children[0].astext()
            if name := self.re_param.findall(field_name):
                # TODO handle python check of correct named arg/attribute
                if len(name) > 1:
                    raise ValueError(f'Multiple param names: {name}')
                else:
                    name = name[0]
                if name in params:
                    raise KeyError(f'Duplicate parameter: {name}')
                if name in types: # Make ArgDoc w/ paired type
                    params[name] = ArgDoc(
                        name=name,
                        description=field.children[1].astext(),
                        type=types[name].type,
                        default=types[name].default,
                    )
                else: # Make initial ArgDoc w/o type
                    params[name] = ArgDoc(
                        name=name,
                        description=field.children[1].astext(),
                    )
            elif name := self.re_type.findall(field_name):
                if len(name) > 1:
                    raise ValueError(f'Multiple type param names: {name}')
                else:
                    name = name[0]
                if name in types:
                    raise KeyError(f'Duplicate parameter type: {name}')

                # TODO support dataclass format: param = default -> type
                type_str = field.children[1].astext()
                parsed_types = self.re_typedoc.findall(type_str)

                if len(parsed_types) < 1:
                    raise ValueError(f'No type found in parsing: {type_str}')

                if parsed_types[-1][1]:
                    # TODO make the actual object, not its str
                    default = get_object(obj, parsed_types[-1][1])
                else:
                    default = ValueExists.false

                found_types = []
                for found, _ in parsed_types:
                    found_types.append(get_object(obj, found))

                if len(found_types) > 1:
                    found_types = MultiType(set(found_types))
                else:
                    found_types = found_types[0]

                # Update the params and types
                if name in params:
                    # Update the existing ArgDoc.
                    types[name] = ValueExists.true
                    params[name].type = found_types
                    params[name].default = default
                else:
                    # Save the partially made parameter doc for later.
                    types[name] = ArgDoc(
                        name=name,
                        description=ValueExists.false,
                        type=found_types,
                        default=default,
                    )
            elif field_name == 'returns':
                if isinstance(returns, BaseDoc):
                    if returns.name == 'returns': # only set here
                        raise KeyError('Multiple `returns` fields exist!')
                    returns.name = 'returns'
                    returns.description = field.children[1].astext()
                else:
                    returns = BaseDoc(
                        'returns',
                        description=field.children[1].astext(),
                    )
            elif field_name == 'rtype':
                if isinstance(returns, BaseDoc):
                    if returns.name != 'returns' \
                        or returns.type != ValueExists.false:
                        raise KeyError('Multiple `rtype` fields exist!')
                    # TODO Namespace grabbing of types... not just store str
                    returns.type = get_object(obj, field.children[1].astext())
                else:
                    # TODO Namespace grabbing of types... not just store str
                    returns = BaseDoc(
                        '',
                        get_object(obj, field.children[1].astext()),
                    )

        # Any unmatched pairs of params and types raises an error
        if xor_set := set(types) ^ set(params):
            raise ValueError(' '.join([
                'There are unmatched params and types in the docstring:',
                f'{xor_set}',
            ]))

        # Return the Function Docstring Object that stores the docsting info
        return FuncDocstring(
            name=obj.__name__,
            type=FunctionType,
            description=description,
            args=params,
            returns=returns,
        )

    def parse_class(
        self,
        obj,
        name=None,
        obj_type=ValueExists.false,
        methods=None,
    ):
        """Parse the given class, obtaining its attributes and given functions.

        Args
        ----
        obj : object
            The class object whose docstring and whose methods' docstrings are
            to be parsed.
        name : str = None
            name to assign to this object's ClassDocstring.
        obj_type : type = None
        methods : [str] = None
            Additional methods whose docstrings are to be parsed.
        """
        docstring = self._parse_initial(obj.__doc__)

        # Obtain the description of the class.
        if first_section := self.re_section.search(docstring):
            # Extract the text from beginning to first section
            description = docstring[:first_section.span()[0]]
        else:
            # There are no sections in the class docstring, so it is all desc.
            description = docstring

        # TODO parse Attributes, optional, unless a dataclass or dataclass-like

        # Obtain the class' __init__ docstring
        init_obj = getattr(obj, '__init__')
        if not init_obj.__doc__:
            # TODO if __init__ does not have a docstring or no args but
            # Attributes does and the attribute names match the init's arg
            # names, then simply use the attribute docstrings as the args,
            # assuming it is like a dataclass w/ generated init.

            # TODO Related, allow for only partially defined args if the others
            # are like dataclass values (when actually a dataclass, able to be
            # checked. This check could include if the arg is used to assign to
            # the attribute without any change to its value (attrib = arg).
            raise NotImplementedError(
                'init w/o docstrings are not supported yet.'
            )
        else:
            init_docstr = self.parse_func(init_obj)

        # Parse all given method docstrings
        if methods:
            method_docstrs = {}
            for method in methods:
                if not hasattr(obj, method):
                    raise KeyError(f'`obj` `{obj}` does not have method {method}')

                method_obj = getattr(obj, method)
                if not callable(method_obj):
                    raise TypeError(
                        f'`{obj}.{method}` is not callable: {method_obj}`'
                    )

                method_docstrs[method] = self.parse_func(method_obj)
        else:
            method_docstrs = None

        return ClassDocstring(
            obj.__name__,
            type(obj),
            description,
            attributes=None, # TODO
            init=init_docstr,
            methods=method_docstrs,
        )

    def parse(
        self,
        obj,
        name=None,
        obj_type=None,
        methods=None,
        style=None,
        doc_linking=False,
    ):
        """General parsing of a given object with a __doc__ attribute.

        Args
        ----
        obj : object | str
            The object whose __doc__ is to be parsed. If a str object of the
            docstring, then the `name` and `obj_type` parameters must be
            provided.
        name : str = None
            The name of the object whose docstring is being parsed. Only needs
            to be supplied when the `obj` is a `str` of the docstring to be
            parsed, otherwies not used.
        obj_type : type = None
            The type of the object whose docstring is being parsed. Only needs
            to be supplied when the `obj` is a `str` of the docstring to be
            parsed, otherwies not used.
        methods : [str] = None
            A list of method names whose docstrings are all to be parsed and
            returned in a hierarchical manner encapsulating the hierarchical
            docstring of a class.  Only used when `obj` is a class object.
        style : str, default None
            Expected docstring style determining how to parse the docstring.
        doc_linking : bool = False
            Linked docstring whose content applies to this docstring and will
            be parsed recursively.

            TODO Add whitelisting of which packages to allow recursive doc
            linking

        Returns
        -------
        FuncDocstring | ClassDocstring
            A Docstring object containing the essential parts of the Docstring,
            or a ClassDocstring which contains the Docstring objects of the
            methods of the class along with the class' parsed Docstring object.
        """
        # TODO optionally parallelize the parsing, perhaps with Ray?
        if isinstance(obj, str):
            if name is None or obj_type is None:
                raise ValueError(' '.join([
                    'If `obj` is a `str` then must also give `name` and',
                    '`obj_type`',
                ]))
        elif hasattr(obj, '__doc__') and hasattr(obj, '__name__'):
            # Obtain info from the object itself
            name = obj.__name__
            obj_type = type(obj)
        else:
            raise TypeError(' '.join([
                'Expected `obj` to be an object with `__doc__` and `__name__`',
                'attributes, or a `str` with the `name` and `obj_type`',
                'parameters given.',
            ]))

        # TODO if a class, then parse the __init__ too, but as the main
        # docstring of interest. As it defines the params to give, and thus
        # the args we care about.
        if isinstance(obj, FunctionType):
            return self.parse_func(obj, name)

        # elif isinstance(obj_type, type): TODO raise if not class object?
        # TODO handle detection of methods, have option ot find those with
        # docs, warn when encountering those without docs.
        return self.parse_class(obj, name, obj_type)


def parse(obj, *args, **kwargs):
    """Parses the object with the expected doc_style.
    Args
    ----
    style : 'numpy' | 'google' | 'rest' | str
        The docstring style to expect when parsing. Default choices are
        {'numpy', 'google', 'rest'}, although any string may be given as long
        as there is a sphinx style conversion extention available.
    obj : object
        The object whose __doc__ is to be parsed.
    """
    # Create parser given doc_style
    parser = DocstringParser(*args, **kwargs)

    # Parse the object's docstring and return the tokenized results.
    return parser.parse(obj)
