"""Code for managing docstring parsing and conversion."""
from enum import Flag, unique
from collections import OrderedDict
from copy import deepcopy
from dataclasses import dataclass, InitVar
from keyword import iskeyword
import re
from typing import NamedTuple

import docutils
from docutils import nodes
from docutils.parsers import rst
from sphinx.ext.autodoc import getdoc, prepare_docstring
from sphinx.ext.napoleon import Config, GoogleDocstring, NumpyDocstring

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

@unique
class ValueExists(Flag):
    """Enum for standing in for a non-existent default value."""
    true = True
    false = False


class MultiType(object):
    """A list of multiple types for when a variable may take multiple types."""
    def __init__(self, types):
        if not isinstance(types, list) and not isinstance(types, tuple):
            raise TypeError(
                f'types must be a list or tuple, not: {type(types)}'
            )
        self.types = types


# Docstring object that contains the parts of the docstring post parsing
# TODO For each of these dataclasses, make them tokenizers for their respective
# parts of the docstring and string call them during parsing
@dataclass
class VariableDoc:
    """Dataclass for return objects in docstrings."""
    name : InitVar[str]
    description : str
    type : type = ValueExists.false

    def __post_init__(self, name):
        if name.isidentifier() and not iskeyword(name):
            self.name = name
        else:
            raise ValueError(f'`name` is an invalid variable name: `{name}`')


@dataclass
class ParameterDoc(VariableDoc):
    """Dataclass for parameters in docstrings."""
    default : InitVar[object] = ValueExists.false

    def __post_init__(self, default):
        # TODO generalize this by extending InitVar to perform this in init.
        # Default the "empty" value to None, possibly removing need to specify
        # `= None` in the dataclass part. Just to expedite this cuz it is now
        # repeated in this code, which itself is meant to expedite through
        # write once... Probably would not inherity from InitVar, but do
        # something similar-ish. Moreso generate the code snippet in the
        # generated __init__(). could possibly even reorder positional args
        # based on the order of inheritance.
        if default is None:
            raise TypeError(' '.join([
                'ParameterDoc() missing 1 required positional argument:',
                '`default` Provide via keyword, if able to through position.',
            ]))
        self.default = default


@dataclass
class Docstring(VariableDoc):
    """Docstring components.

    Attributes
    ----------
    short_description : str
        The short description of the docstring.
    args : str
        The function's Arguments/Parameters or the class' Attributes.
    """
    short_description : InitVar[str] = None
    other_sections: OrderedDict({str : str}) = None

    def __post_init__(self, short_description):
        if short_description is None:
            raise TypeError(' '.join([
                'Docstring() missing 1 required positional argument:',
                '`short_description` Provide via keyword, if able to through',
                'position.',
            ]))
        self.short_description  = short_description


@dataclass
class FuncDocstring(Docstring):
    """Function docstring components.

    Attributes
    ----------
    short_description : str
        The short description of the docstring.
    args : str
        The function's Arguments/Parameters or the class' Attributes.
    """
    args : InitVar[OrderedDict({str : ParameterDoc})] = None
    other_args : OrderedDict({str : ParameterDoc}) = None # TODO implement parsing
    return_doc : VariableDoc = ValueExists.false

    def __post_init__(self, args):
        if args is None:
            raise TypeError(' '.join([
                'FuncDocstring() missing 1 required positional argument:',
                '`args` Provide via keyword, if able to through position.',
            ]))
        self.args  = args

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
    """The multiple Docstrings the make up a class, including at least the
    class' docstring and the __init__ method's docstring.
    """
    attributes : InitVar[OrderedDict({str : ParameterDoc})] = None
    init_docstring : InitVar[FuncDocstring] = None
    methods : {str: FuncDocstring} = None

    def __post_init__(self, attributes, init_docstring):
        # TODO attributes are unnecessary for config. uses init or load.
        #if attributes is None:
        #    raise TypeError(' '.join([
        #        'ClassDocstring() missing 1 required positional argument:',
        #        '`attributes` Provide via keyword, if unable to through',
        #        'position.',
        #    ]))
        self.attributes  = attributes

        if init_docstring is None:
            raise TypeError(' '.join([
                'ClassDocstring() missing 1 required positional argument:',
                '`init_docstring` Provide via keyword, if unable to through',
                'position.',
            ]))
        self.init_docstring  = init_docstring


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


class InitialParse(NamedTuple):
    """The results of the parsing of the beginning of a docstring object."""
    docstring: str
    short_description: str


class DocstringParser(object):
    """Docstring parsing.

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
        style : {'rst', 'numpy', 'google'}
            The style expected to parse.
        doc_linking : bool = False
            Not Implemented Yet
        config : sphinx.ext.napoleon.Config = None
            Not Implemented Yet
        """
        if (style := style.lower()) not in {'rst', 'numpy', 'google'}:
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
        self.re_field = re.compile(':[ \t]*(\w[ \t]*)+:')
        self.re_directive = re.compile('\.\.[ \t]*(\w[ \t]*)+:')
        self.re_section = re.compile(
            '|'.join([self.re_field.pattern, self.re_directive.pattern])
        )

        # Temporary useful patterns
        section_end_pattern = f'({self.re_section.pattern}|\Z)'
        name_pattern = '[ \t]+(?P<name>[\*\w]+)'
        doc_pattern = f'[ \t]*(?P<doc>.*?)({section_end_pattern})'

        # TODO Create unit tests to ensure the name & doc patterns extract
        # appropriately.

        # Regexes for checking and parsing the types of sections
        #self.re_param = re.compile(f':param{name_pattern}:{doc_pattern}', re.S)
        self.re_param = re.compile(f'param{name_pattern}', re.S)
        self.re_type = re.compile(f':type{name_pattern}:{doc_pattern}', re.S)

        # For parsing the inner parts of a parameter type string.
        # Captures the type or multi-types as a list
        self.re_default = re.compile(
            '(?<=|,[ \t]*default)[ \t]*(?P<default>[^\s]+)'
        )
        # Must be applied after default match is removed
        self.re_typedoc = re.compile('(?:[ \t]*\|[ \t]*)*(\w[\w\.]*)', re.S)

        self.re_returns = re.compile(':returns:{doc_pattern}', re.S)
        self.re_rtype = re.compile(':rtype:{doc_pattern}', re.S)

        self.re_attribute = re.compile(
            f'\.\.[ \t]*attribute[ \t]*::{name_pattern}[ \t]*\n{doc_pattern}',
            re.S,
        )
        # TODO extract attribute type ':type: <value>\n'
        #   Need to fix doc pattern here... this is wrong.
        self.re_attr_type = re.compile('[ \t]+:type:{doc_pattern}', re.S)

        #self.re_other_params = re.compile()

        self.re_rubric = re.compile(
            f'\.\.[ \t]*attribute[ \t]*::{name_pattern}[ \t]*\n{doc_pattern}',
            re.S,
        )

        # Register AttributeDirective once for this parser.
        rst.directives.register_directive(
            'attribute',
            AttributeDirective,
        )

    def _parse_initial(self, docstring):
        """Internal util for pasring inital portion of docstring."""
        docstring = prepare_docstring(docstring)

        # NOTE for now, use what is specified at initialization
        #style = self.style if style is None else style.lower()
        #doc_linking = self.doc_linking if doc_linking is None else doc_linking

        # Convert the docstring is in reStructuredText styling
        if self.style == 'google':
            docstring = GoogleDocstring(docstring, self.config)
        elif self.style == 'numpy':
            docstring = NumpyDocstring(docstring, self.config)
        # TODO allow the passing of a func/callable to transform custom doc
        # styles

        # TODO parse the RST docstring
        #   TODO find Parameters/Args and other Param like sections.
        #   TODO Get all param names, their types (default to object w/ logging
        #   of no set type), and their descriptions

        if len(docstring) < 1:
            raise ValueError('The docstring is only a short description!')

        # Short description is always the first line only
        short_description = docstring[0]

        docstring = '\n'.join(docstring)

        return InitialParse(docstring, short_description)

    def _obj_defaults(self, obj, name=None, obj_type=ValueExists.false):
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

    def parse_func(self, obj, fname=None, obj_type=ValueExists.false):
        """Parse the docstring of a function."""
        docstring, fname, obj_type = self._obj_defaults(obj, fname, obj_type)
        docstring, short_description = self._parse_initial(docstring)

        # Use docutils to parse the RST
        doc = parse_rst(docstring)

        # TODO optionally set how to handle long descriptions for argparse help
        if long_desc_end_idx := doc.first_child_not_matching_class(
            nodes.paragraph
        ):
            long_description = '\n'.join(
                [ch.astext() for ch in doc.children[:long_desc_end_idx]]
            )

        if not (field_list := doc.first_child_not_matching_class(
            nodes.field_list
        )):
            raise ValueError('The given docstring includes no fields!')

        # The field list includes params, types, returns, and rtypes,
        field_list = doc.children[field_list]

        # Prepare the paired dicts for params to catch dups, & missing pairs
        params = OrderedDict()
        types = OrderedDict()
        # Go through the field_list and parse the values.
        for field in field_list:
            field_name = field.children[0].astext()
            if name := self.re_param.findall(field_name):
                if name in params:
                    raise KeyError('Duplicate parameter!')
                if name in types:
                    params[name] = ParameterDoc(
                        name=name,
                        description=field.children[0][1].astext(),
                        type=types[name].type,
                        default=types[name].default,
                    )
                else:
                    params[name] = ParameterDoc(
                        name=name,
                        description=field.children[0][1].astext(),
                    )
            elif name := self.re_type.findall(field_name):
                if name in types:
                    raise KeyError('Duplicate parameter type!')

                # TODO type parser: [type[| type]*][ = [default]][, optional]
                #   thus requiring a multi-type object, just a special class
                #   that encapsulates a list.
                # TODO support dataclass format: param = default -> type
                type_str = field.children[0][1].astext()

                # Parse default first & remove to get the re multi-type to work
                if default := self.re_default.search(type_str):
                    span = default.span()
                    default = self.re_default.findall(
                        type_str[span[0]:span[1]]
                    )[0]

                    type_str = type_str[:[0]]
                else:
                    default = ValueExists.false

                parsed_type = self.re_typedoc.findall(type_str)

                if len(parsed_type) < 1:
                    raise SyntaxError('No type found.')

                for found in parsed_type:
                    if '.' in found and not all(
                        [part.isidentifier() for part in found.split('.')]
                    ):
                        raise ValueError(
                            'Parameter type consists of not identifier parts'
                        )
                    elif iskeyword(found):
                        raise ValueError(
                            'The parameter type cannot be a keyword!'
                        )

                if len(parsed_type) > 1:
                    parsed_type = MultiType(parsed_type)

                # Update the params and types
                if name in params:
                    # Update the existing ParameterDoc.
                    types[name] = ValueExists.true
                    params[name].type = parsed_type
                    params[name].default = default
                else:
                    # Save the partially made parameter doc for later.
                    types[name] = ParameterDoc(
                        name=name,
                        description=ValueExists.false,
                        type=parsed_type,
                        default=default,
                    )
            # TODO Handle returns, rtype: they will be in same field list,
            # probably

            # Any unmatched pairs of params and types raises an error
            if xor_set := set(types) ^ set(params):
                raise ValueError(' '.join([
                    'There are unmatched params and types in the docstring:',
                    f'{xor_set}',
                ]))

        # Return the Function Docstring Object that stores the docsting info
        return FuncDocstring(
            args=params,
            name=fname,
            description=long_description,
            type=obj_type,
            short_description=short_description,
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
        docstring, name, obj_type = self._obj_defaults(obj, name, obj_type)
        docstring, short_description = self._parse_initial(docstring)

        # Obtain the long_description of the class.
        if first_section := self.re_section.search(docstring):
            # Extract the text from beginning to first section
            long_description = docstring[:first_section.span()[0]]
        else:
            # There are no sections in the class docstring, so it is all desc.
            long_description = docstring

        # TODO parse Attributes, optional, unless a dataclass or dataclass-like

        # Obtain the class' __init__ docstring
        init_obj = getattr(obj, '__init__')
        if init_obj.__doc__ is None:
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
            attributes=None,
            init_docstring=init_docstr,
            methods=method_docstrs,
            name=name,
            description=long_description,
            type=obj_type,
            short_description=short_description,
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
        """
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
        methods : [str], optional
            A list of method names whose docstrings are all to be parsed and
            returned in a hierarchical manner encapsulating the hierarchical
            docstring of a class.  Only used when `obj` is a class object.
        style : str, default None
            Expected docstring style determining how to parse the docstring.
        doc_linking : bool, default False
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
        raise NotImplementedError('Use `parse_class()` or `parse_func()`')

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
        if isinstance(obj_type, type):
            class_docstring = obj.__doc__
            init_docstring = self.parse_func(obj.__init__, '__init__')

            raise NotImplementedError('Need to add parsing of a class')
            # TODO add parsing of a class' methods in given list.
            #return ClassDocstring(name, obj_type, description, )

        return self.parse_func(obj.__doc__, name)#, obj_type)

# TODO Hierarchical Configuration Class given parsed docstring objects.
