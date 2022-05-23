"""Code for parsing docstrings."""
import ast
import builtins
from collections import OrderedDict
from copy import deepcopy
from dataclasses import is_dataclass
#from functools import wraps
from inspect import getmodule, isclass
from importlib import import_module
from keyword import iskeyword
from operator import attrgetter
import re
import sys
from typing import NamedTuple
from types import FunctionType

import docutils
from docutils import nodes
from docutils.parsers import rst
from sphinx.ext.autodoc import getdoc, prepare_docstring
from sphinx.ext.napoleon import Config, GoogleDocstring, NumpyDocstring

from docstr.docstring import (
    get_full_qual_name,
    ValueExists,
    MultiType,
    ArgDoc,
    ClassDocstring,
    FuncDocstring,
    BaseDoc,
    Namespace,
)

import logging
logger = logging.getLogger(__name__)


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
#   NOTE that abstract syntax trees (ast) also supplies the structure of #   classes, funtions, methods, and other syntax trees. When applicable, its
#   use inplace of 3rd party packages may be more desirable since it is
#   supplied by the python standard library.

# TODO note that Factories or module level function that load classes need
# handeld by parsing their docstrings... when automating the loading of
# classes. Just keep it in mind, and note that Factories make sense when the
# sub classes, say a bunch of different torch.modules or tf.keras.models

# TODO optionally set how to handle long descriptions for argparse help.

# TODO possible that getattr should be replaced with inspect.getattr_static in
# some cases.


def duck_test_isinstance_namedtuple(x):
    """Duck test if the given object looks and acts like a namedtuple."""
    return duck_test_issubclass_namedtuple(type(x))


def duck_test_issubclass_namedtuple(type_x):
    """Duck test if the given class / type object looks and acts like a
    namedtuple.

    Note
    ----
    Modified from https://stackoverflow.com/a/2166841/6557057
    """
    bases = type_x.__bases__
    if len(bases) != 1 or bases[0] != tuple:
        return False

    fields = getattr(type_x, '_fields', None)
    if not isinstance(fields, tuple):
        return False

    return all(isinstance(field, str) for field in fields)


def get_namespace_obj(namespace, name, default=ValueExists.false):
    """Given a str of an object's identifier in the given object whose module
    is used as the namespace, returns the object, otherwise returns the default
    if given or raises error."""
    try:
        return getattr(namespace, name)
    except AttributeError as e:
        if '.' in name:
            # TODO handle getting the method of a class; Do error raising
            parts = name.rpartition('.')
            class_obj = getattr(namespace, parts[0])
            return getattr(class_obj, parts[-1])

        if default != ValueExists.false:
            return default
        raise e


def get_builtin(name, default=ValueExists.false):
    """Accesses pythons builtins using a key as a dictionary access via get."""
    return get_namespace_obj(builtins, name, default)


def get_module_object(name, default=ValueExists.false):
    """Gets the object accessible from a global access of `from module import`,
    where the given name of the object is the module joined by periods to the
    actual object, such as f'{__module__}.{__qualname__}'.

    NOTE
    ----
    This can probably be improved, especially the first `except` section.
    """
    try:
        return import_module(name)
    except ModuleNotFoundError as e:
        parts = name.split('.')
        for i in range(1, len(parts)):
            try:
                module = import_module('.'.join(parts[:-i]))
                break
            except ModuleNotFoundError as e:
                continue
        else: # Raise 1st e if no module found at all from name
            if default is not ValueExists.false:
                return default
            raise e
        return attrgetter('.'.join(parts[-i:]))(module)
        # TODO beware that this may return None by default rather than
        # raise an exception!


def get_object(namespace_obj, name, default=ValueExists.false):
    """Given a str of an object's identifier in the given object whose module
    is used as the namespace, returns the object, otherwise returns the default
    if given or raises error. The name is first checked if it is a python
    builtin object, otherwise it will attempt to return the attribute of the
    same given `name` in the module that namespace_obj is contained within.
    If the namespace_obj is a module itself, then it will be used to get the
    attribute `name`.

    Notes
    -----
    First, checks if name is in __builtin__. Then checks if in the module's
    namespace of the object. Then handles when given a str that is an instance
    of an object or a literal. Beware that if the str represntation of an
    instance exists in the namespace, then it is prioritized over the literal
    or object instance.
    """
    #try: # Check if the given str exists in a global context
    try:
        try: # TODO prioritize: literals, locals, globals, then builtins
            return get_builtin(name, default)
        except AttributeError as e_built_in:
            # TODO getmodule does not support all cases! You want to pass the
            # locals() as seen from that args location at the beginning of its
            # code block. The issue arises in the difference between the
            # module's namespace versus locals() within some nested structure.
            return get_namespace_obj(getmodule(namespace_obj), name, default)
    except AttributeError as e_namespace_module:
        try:
            return ast.literal_eval(name)
        #raise NotImplementedError('Informed through `astype` not yet coded.')
        # ast.literal_eval() supports: strings, bytes, numbers, tuples, lists,
        # dicts, sets, booleans, None and Ellipsis.
        except Exception as e_literal_eval:
            #raise NotImplementedError(' '.join([
            #   'Need to support conversion of a str of an object instance or',
            #    'literal to that actual object instance or literal.',
            #]))#.with_traceback(e)

            # TODO handle being given an instance of an object, esp. primitive.
            # When given an instance of an object, if default the type is
            # known, otherwise it is intended to be self-evident and as such
            #except ModuleNotFoundError as e:
            # TODO check if the given thing is an object within a module
            #   if object in module, check if module name.rpartition('.')[0]
            #   exists
            #       This works if the module is right before the object If the
            #       object is a function within a class, this requires a [:-2]
            #       of last '.' check.
            return get_module_object(name)


class AttributeName(nodes.TextElement):
    """Contains the text of the attribute type."""
    pass


class AttributeType(nodes.TextElement):
    """Contains the text of the attribute type."""
    pass


class AttributeBody(nodes.Structural, nodes.Element):
    """Contains the AttributeType and paragraph body of an attribute."""
    pass


# TODO Attribute List, much like field list.
#class AttributeList(nodes.Structural, nodes.Element):
#    """Contains a lis of AttributeBody objects."""
#    pass


class AttributeDirective(rst.Directive):
    """ReST parser for python class docstring attributes."""
    required_arguments = 1
    optional_arguments = 1
    has_content = True

    def run(self):
        # Raise an error if the directive does not have contents.
        try:
            self.assert_has_content()
            is_see_linking = False
        except Exception as e:
            if self.arguments[0] != 'see' or len(self.arguments) < 2:
                raise ValueError(
                    'Attribute Directive has no content and the first '
                    "argument is not 'see' or there are less than 2 arguments "
                    'parsed. `AttributeDirective` parsed arguments = '
                    f'{self.arguments}'
                ) from e
            is_see_linking = True

        node = AttributeBody()
        name_node = AttributeName()
        name_node += nodes.Text(self.arguments[0])
        node += name_node

        if is_see_linking:
            type_node = AttributeType()
            type_node += nodes.Text(' '.join(self.arguments[1:]))
            node += type_node
        else:
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
                raise ValueError(f'No attribute type for {self.arguments[0]}!')

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


class DocstringParser(object):
    """Docstring parser for a specific style and parser config.

    Attributes
    ----------
    style : {'rst', 'numpy', 'google'}
        The style expected to parse.
    doc_linking : bool = False
    config : sphinx.ext.napoleon.Config = None
    parsed_tokens : dict(str: DocString)
        The already parsed tokens such that they are accessible by their fully
        qualified name as in python to expedite future doc parsing due to doc
        linking by avoiding reparsing docstrings.

        When an object is encountered to be parsed, it is added to this
        dictionary with a value of ValueExists.false to denote it is in the
        process of being parsed. This means only objects with __doc__ are
        included here, not individual ArgDocs.

        Should we do this? Naw, use fully qualified python name for simplicity
        This object is structured such that the root docstr namespace is the
        root of this parsed token tree. This is traversable via namespace
        calling, e.g., `parsed_class.parsed_argument`. So if a function, the
        arguments are able to be accessed from `function.arg1`. If a class,
        the arguments to the init method are able to be called as
        `class.__init__.arg` and attributes as `class.attr`.
    namespace : Namespace = None
        The root namespace of this docstr parser. It will expand as the parser
        progresses. It is preset in the case of a docstr configuraiton file's
        imports. If there is no hit in the namespace of the docstring's own
        module, then this is used.

        Set to None when there is no additional namespace information.
        TODO: for now, expect all docstrings encountered to specify thier own
        expected namespaces and things for objects.
    """
    def __init__(
        self,
        style,
        whitelist=None,
        #TODO blacklist=None,
        recursion_limit=None,
        config=None,
    ):
        """
        Args
        ----
        style : 'numpy' | 'google' | 'rest' | str
            The docstring style to expect when parsing. Default choices are
            {'numpy', 'google', 'rest'}, although any string may be given as
            long as there is a sphinx style conversion extention available.
        recursion_limit : int = 0
            The maximum allowed number of recursive function calls to
            `self.parse()` either due to types being objects with docstrings to
            parse or due to doc linking with `see`.
        config : sphinx.ext.napoleon.Config = None
            Not Implemented Yet
        whitelist: {str} = None
            Whitelisted modules or objects by their str fully qualified
            namespace identifier, meaning no other objects outside said modules
            may be parsed. If a module, anything within that module's namespace
            may be parsed. If not a module, that specific object may be parsed.
        blacklist: {str} = None
            Blacklisted objects by their str namespace identifier, meaning
            these objects will not be parsed. If given a module, then the
            entire hierarchy below it will be ignored.
        """
        style = style.lower()
        if style not in {'rst', 'numpy', 'google'}:
            raise ValueError(
                "Expected `style` = 'rst', 'numpy', or 'google', not `{style}`"
            )

        # TODO allow the passing of a func/callable to transform custom doc
        # styles, thus allowing users to easily adapt to their doc style

        self.style = style

        if whitelist is None or isinstance(whitelist, set):
            self.whitelist = whitelist
        else:
            raise TypeError(f'`whitelist` type `set`, not {type(whitelist)}')

        if recursion_limit is None:
            self.recursion_limit = sys.getrecursionlimit()
        elif isinstance(recursion_limit, int):
            self.recursion_limit = recursion_limit
        else:
            raise TypeError(
                f'recursion_limit type `int`, not {type(recursion_limit)}'
            )

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
        name_pattern = r'[ \t]+(?P<name>[\*\w.]+)'
        # Non-Greedy kleene star
        doc_pattern = fr'[ \t]*(?P<doc>.*?)({section_end_pattern})'

        # Regexes for checking and parsing the types of sections
        self.re_name = re.compile(name_pattern)

        #self.re_param = re.compile(fr'param({name_pattern})+')
        #self.re_type = re.compile(fr':type{name_pattern}:{doc_pattern}', re.S)
        # docutils splits name and doc pattern into field name and field body
        #self.re_type = re.compile(fr'type{name_pattern}')

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

        self.parsed_tokens = {}
        #if namespace:
        #   self.namespace = {for n in namespace}
        #else:
        self.namespace = None

    def _get_object(self, namespace_obj, name, default=ValueExists.false):
        """Wraps get_object with a fallback to this parser's namespace"""
        try:
            obj_instance = get_object(namespace_obj, name, default)
        except Exception as e:
            # TODO add the above exception to the stack trace of the following
            #.with_traceback(e)

            # TODO ignoring doing this here (if persists, rm this function)
            # because you can check qual name of object once recieved to see if
            # it should be parsed based on whitelist or other conditions.
            if self.namespace is not None:
                obj_instance = get_namespace_obj(self.namespace, name, default)

        try:
            if obj_instance is None and name != 'None':
                raise ValueError(' '.join([
                    'DocstringParser._get_object() got `None` as object',
                    "instance and name is not 'None'",
                    f'\nnamespace_obj = {namespace_obj}\n',
                    f'name = {name}',
                ]))
        except UnboundLocalError as e:
            raise ValueError(' '.join([
                'DocstringParser._get_object() could not get object instance',
                f'\nnamespace_obj = {namespace_obj}\n',
                f'name = {name}',
            ])) from e

        return obj_instance

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

    def parse_attr_list(self, obj, attrib_bodies):
        # TODO redesign this parsing to be sane and not a mess wrt func calls
        args = OrderedDict()
        recursive_parse = {}
        for attrib_body in attrib_bodies:
            if not isinstance(attrib_body, AttributeBody):
                continue
            name = attrib_body[0].astext()

            if name in args:
                raise KeyError(' '.join([
                    'Duplicate attribute for class',
                    f'`{get_full_qual_name(obj)}`: `{name}`',
                ]))

            type_str = attrib_body[1].astext()
            parsed_types = self.re_typedoc.findall(type_str)

            num_parsed_types = len(parsed_types)
            if num_parsed_types < 1:
                raise ValueError(' '.join([
                    'No type found in parsing class',
                    f'`{get_full_qual_name(obj)}`, attribute `{name}`:',
                    f'{type_str}',
               ]))

            if parsed_types[-1][1]:
                default = self._get_object(obj, parsed_types[-1][1])
            else:
                default = ValueExists.false

            # TODO Store docstring linking for this argument's ArgDoc
            """
            if parsed_types[0][0] == 'see':
                if num_parsed_types == 2:
                    doc_linking[name] = (parsed_types[1][0], None)
                elif num_parsed_types == 3:
                    doc_linking[name] = (
                        parsed_types[1][0],
                        parsed_types[2][0],
                    )
                elif num_parsed_types > 3:
                    raise ValueError(
                        f'More than 3 elements for doc linking: {type_str}'
                    )
                continue # TODO handle dups/missing type/param check
            """

            found_types = []
            for found, _ in parsed_types:
                found_types.append(self._get_object(obj, found))

            if len(found_types) > 1:
                found_types = MultiType(found_types)
            else:
                found_types = found_types[0]
                if self.whitelist:
                    if found_types is None:
                        recursive_parse[name] = found_types
                    else:
                        try:
                            ft_qname = get_full_qual_name(found_types)
                        except Exception as e:
                            raise ValueError(' '.join([
                                '`found_types` has unexpected value',
                                f'`{found_types}` for attribute `{name}`',
                            ])) from e
                        if ft_qname in self.whitelist:
                            recursive_parse[name] = found_types

            if len(attrib_body) > 2:
                description = attrib_body[2].astext()
            else:
                description = ValueExists.false
                logger.debug('name = %s', name)
                logger.debug('description = %s', description)
                logger.debug('found_types = %s', found_types)
                logger.debug('default = %s', default)
                logger.debug('args = %s', args)

            args[name] = ArgDoc(
                name=name,
                description=description,
                type=found_types,
                default=default,
            )
        return args, recursive_parse

    def parse_recursive_see_all(
        self,
        obj,
        qualified_name,
        params,
        types,
        see_args_count,
        parent=None,
        recursion_limit=0,
    ):
        """Logic for handling recursive parsing step to finish an object's
        parsing. This is for handling the linking of all args or attirbutes
        from the given object to this current object.

        Returns
        -------
        OrderedDict
            The parameters `params` after being filled with the recursively
            parsed content.
        """
        # En masse args doc linking from an object's __doc__
        ordered_params = []
        growing_arg_set = set(params.keys())
        linked_obj_set = set()
        for i in range(see_args_count):
            see_name = f'see_{i}'
            growing_arg_set.remove(see_name)

            # Preserve parsed args order
            if next(iter(params)) == see_name: # see name is first
                see_params = params.popitem(last=False)[1]
            elif next(reversed(params)) == see_name: # see name is last
                see_params = params.popitem()[1]
                ordered_params.append(params)
            else: # Must iterate through and find see_name, probs rarest case.
                save_params = params.popitem(last=False)
                save_params = OrderedDict({save_params[0]: save_params[1]})
                key, value = params.popitem(last=False)
                while key != see_name:
                    save_params[key] = value
                    key, value = params.popitem(last=False)
                ordered_params.append(save_params)
                see_params = value

            for linked_obj in see_params:
                if linked_obj in linked_obj_set:
                    raise ValueError(' '.join([
                        'Duplicate linked object `{linked_obj}` found when',
                        f'parsing `{qualified_name}`',
                    ]))
                if linked_obj == 'self':
                    if not isinstance(parent, OrderedDict):
                        raise TypeError(
                            'Given parent `see self` is not an OrderedDict '
                            #'nor a ClassDocstring
                            'when parsing object '
                            f'`{qualified_name}`, instead' f'given parent is '
                            f'type `{type(parent)}`.'
                        )
                    parsed_args = deepcopy(parent)
                else:
                    parsed_obj = self.parse(
                        self._get_object(obj, linked_obj),
                        recursion_limit=recursion_limit + 1,
                    )
                    if isinstance(parsed_obj, ClassDocstring):
                        parsed_args = parsed_obj.attributes
                    else: # FuncDocstring
                        parsed_args = parsed_obj.args

                # Check for duplicates and update unique args and linked_objs
                if dups := growing_arg_set & parsed_args.keys():
                    raise ValueError(' '.join([
                        'Duplicate arg name found when adding parsed args',
                        f'from linked object `{linked_obj}` to current object',
                        f'`{qualified_name}`: {dups}',
                    ]))
                growing_arg_set |= parsed_args.keys()
                linked_obj_set.add(linked_obj)

                ordered_params.append(parsed_args)

            # Ensure all added args are within type for future type checking.
            for key in growing_arg_set - types.keys():
                types[key] = ValueExists.true

        # If any params follow last see, append them to ordered_params
        if params:
            ordered_params.append(params)

        # Reconstruct ordered params from the multiple param ordered dicts
        if ordered_params:
            new_params = OrderedDict()
            for op in ordered_params:
                new_params.update(op)
            params = new_params

        return params

    def parse_recursive_see_specific(
        self,
        recursive_parse,
        doc_linking,
        qualified_name,
        params,
        types,
        parent=None,
        recursion_limit=0,
    ):
        """Modifies params and types in place with the parsed specifc args
        linked via see .
        """
        # TODO Recursively parse docs of valid types w/in whitelist, error o.w.
        for arg, linked_obj in recursive_parse.items():
            #raise NotImplementedError('Recursive parse of objects w/in types')
            # TODO at every _get_object, there is a chance that the object is
            # An object able to be configured.

            # Check if in whitelist, error otherwise
            #if qname not in self.whitelist:
            #    raise ValueError(
            #        f'Object not in whitelist for recursive parse: {qname}'
            #    )

            # Recursively parse the object
            params[arg].type = self.parse(
                linked_obj,
                recursion_limit=recursion_limit + 1,
            )
            # TODO Update params and types once parsed.

        parent_qname = qualified_name.rpartition('.')[0]

        # TODO if any see ``, do first, preserve order, and note when dupes
        # requested: same attribute, not multiple similar args to same see.

        # TODO Perform depth first traversal specific arg doc linking via see.
        for name, (linked_obj, arg_name) in doc_linking.items():
            # TODO if already parsed, use that docstr item.
            #   1. see another arg in the same docstr (will be parsed by now)
            #       This applies for `self` when in class' docstr, otherwise
            #       this checks if an already parsed docstring exists.
            #       Probably should prevent silly multi-hop sees in this case.
            #   2. see an arg in `self` (the class' attributes of `name`)
            #       In case of __init__, likely attributes already parsed.
            #       If not, then grab class' docstr from this obj. If not a
            #       method then throw an error.
            #   3. see an arg that has been parsed by this parser, requires a
            #       "global" context from this parser's instance (self).

            # TODO if not already parsed, parse arg_name in given object's doc
            #   - TODO early exit parsing when only one arg is required.


            # TODO 1. check local (in this object)
            # TODO 2. check obj's module for linked_obj
            # TODO 3. check if a fully qualified name
            # Obtain the full qualified name of the linked object.
            #qname = TODO

            # TODO note that the final item on the namespace chain could be an
            # attribute of a class or an argument! We probably do not want to
            # support linked_obj arg_name to avoid unnecessry expressivity and
            # keep with following standards for namespaces.

            if linked_obj == 'self': # Set qname to the class object of method
                # Keeping full qname up to class, rm the last function.
                # NOTE this assumes that the parent of this object is the
                # class that contains the invoked `self`. There are cases
                # where this is not the case, but uncertain if common or
                # desired to be handled. If the class is already parsed,
                # then this can be handled within docstr parsing,
                # otherwise, one would have to find the corret class within
                # the module, but nesting makes this very difficult and
                # leaves the realm of regular grammars.

                if parent: # Given parent class attributes from parse_class
                    parent_attr = parent
                    if not isinstance(parent_attr, OrderedDict):
                        raise TypeError(' '.join([
                            'Given parent `see self` is not an',
                            'OrderedDict when parsing object',
                            f'`{qualified_name}`, instead',
                            f'given parent is type `{type(parent)}`.'
                        ]))
                elif parent in self.parsed_tokens: # Class is already parsed.
                    parent_attr = self.parsed_tokens[parent_qname]

                    if not isinstance(parent_attr, ClassDocstring):
                        raise TypeError(' '.join([
                            'Parent is not a Class when using `see self`',
                            f'in `{qualified_name}`, instead',
                            f'parent is type `{type(parent_attr)}`.'
                        ]))
                    parent_attr = parent_attr.attributes
                else:
                    # Parse the class
                    parent_attr = self.parse_class(
                        get_module_object(parent_qname),
                        recursion_limit=recursion_limit+1,
                        parse_init=False,
                    ).attributes

                    # 1. Parse class w/ placeholder for init.
                    # 2. Take attributes from it.
                    # 3. Put incomplete parsed class (missing only init) in
                    # place to finish.
                    # 4. After finishing a pass of parsing, check if incomplete
                    # classes to finish.

                if arg_name:
                    parsed_arg = deepcopy(parent_attr[arg_name])
                    parsed_arg.name = name
                else: # arg name pass through: same name in parent.
                    parsed_arg = deepcopy(parent_attr[name])

                # TODO support override of default
                # TODO support memory efficient view w/ override of values

                if name in params and params[name].description:
                    # Description override exists
                    parsed_arg.description = params[name].description

                # Ensure paired type and param check will pass.
                params[name] = parsed_arg
                types[name] = ValueExists.true
            else:
                raise NotImplementedError(' '.join([
                    f'Doc linking w/o `see self`. Linked `{linked_obj}`',
                    f'in parsing `{qualified_name}`.',
                ]))

            """
            # Throw error if infinite looping of doc linking
            elif qname in self.parsed_tokens:
                if self.parsed_tokens[qname] == ValueExists.false:
                    raise ValueError(
                        f'`{qname}` is parsing. Infinite Loop in doc linking.'
                    )
                # Use the parsed object to complete or as the ArgDoc
                raise NotImplementedError('Doc linking to parsed token.')
            else: # TODO New, unencountered object to be parsed, recursively
                linked_obj = self._get_object(correct_namespace, linked_obj)
                self.parse(linked_obj, recursion_limit=recursion_limit + 1)
            """
        #return params

    def parse_desc_args_returns(self, obj, recursion_limit=0, parent=None):
        """Parse the docstring of a function.

        Args
        ----
        obj : object | str
            The object whose __doc__ is to be parsed.
        recursion_limit : int = 0
            Integer that depicts the recursive depth of this current parse.
        parent : OrderedDict(str: ArgDoc)
            The attributes of a class serving as the parent object to `obj`.

        Returns
        -------
        (
            str,
            OrderedDict(str:docstring.ArgDoc) = None,
            ValueExists.false | docstring.BaseDoc
        )
            The description string, parsed args or attributes, and returns.

        Notes
        -----
        This should really be a one pass parse for everything that just handles
        the context when it occurs. Otherwise, may remove the checks for
        returns in the loop of fields when in class docstrings for a slight
        speed increase.
        """
        docstring = self._parse_initial(obj.__doc__)
        # Use docutils to parse the RST (one pass... followed by more.)
        doc = parse_rst(docstring)

        qualified_name = get_full_qual_name(obj)

        if description := doc.first_child_not_matching_class(nodes.paragraph):
            description = '\n'.join(
                [ch.astext() for ch in doc.children[:description]]
            )
        else:
            description = ValueExists.false

        if (field_list := doc.first_child_matching_class(
            nodes.field_list
        )) is None:
            # No fields
            if (field_list := doc.first_child_matching_class(
                AttributeBody
            )) is None:
                # No Attribute Body
                raise ValueError(
                    f'Given docstring includes no fields: `{qualified_name}`'
                )
            else:
                # TODO replace quick HACK, this expects the remainder be attr
                # Seems good to separate func and attr parsing if not same
                # format. Though, I could possibly make them the same format
                # since i control how Attributes are parsed, as above in
                # AttirbuteDirective.
                args, recursive_parse = self.parse_attr_list(
                    obj,
                    doc.children[field_list:],
                )

                for arg, linked_obj in recursive_parse.items():
                    # Recursively parse the object
                    if arg != 'see':
                        args[arg].type = self.parse(
                            linked_obj,
                            recursion_limit=recursion_limit + 1,
                        )
                    else:
                        # TODO This fundamnetally does not handle multiple
                        # sees. this is why i want attribs and args to have
                        # same format so i can reuse the code from args for
                        # this.
                        args.pop('see')
                        linked_obj = self.parse(
                                linked_obj,
                                recursion_limit=recursion_limit + 1,
                                #parent=args,
                            )
                        if isinstance(linked_obj, FuncDocstring):
                            args.update(linked_obj.args)
                        elif isinstance(linked_obj, ClassDocstring):
                            args.update(linked_obj.attributes)
                        else:
                            raise TypeError(
                                f"`see` in `{qualified_name}`'s attribs "
                                'links to unsupported parsed docstring '
                                f'type: {type(linked_obj)}'
                            )

                        # TODO handle making this obj's description that of
                        # the linked obj when it is NOT the only arg.
                        # Perhaps, modify description to include a notice
                        # that it was copy pasted from the linked obj given
                        # no description existed in the active obj.
                        if description == ValueExists.false:
                            description = linked_obj.description
                return description, args, ValueExists.false
        else:
            # The field list includes params, types, returns, and rtypes,
            field_list = doc.children[field_list]

        # TODO doc linking of ALL args/attr from linked object.
        self.parsed_tokens[qualified_name] = ValueExists.false

        # Prepare the paired dicts for params to catch dups, & missing pairs
        params = OrderedDict()
        types = OrderedDict()
        recursive_parse = {}
        doc_linking = OrderedDict() # Traversal of docstrings args via `see`
        see_args_count = 0
        returns = ValueExists.false

        # Go through the field_list and parse the values.
        for field in field_list:
            field_name = field.children[0].astext()
            if field_name[:5] == 'param':
                name = self.re_name.findall(field_name)
                # TODO handle python check of correct named arg/attribute
                if name[0] == 'see':
                    params[f'see_{see_args_count}'] = name[1:]
                    see_args_count += 1
                    continue
                elif len(name) > 1:
                    raise ValueError(' '.join([
                        'Multiple param names for param of object',
                        f"`{qualified_name}`: `{name}`",
                    ]))
                else:
                    name = name[0]
                if name in params:
                    raise KeyError(' '.join([
                        f'Duplicate parameter for object `{qualified_name}`:',
                        f'`{name}`',
                    ]))
                elif name in types: # Make ArgDoc w/ paired type
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
            elif field_name[:4] == 'type':
                name = self.re_name.findall(field_name)
                if len(name) > 1:
                    raise ValueError(' '.join([
                        f'Multiple type param names for object ',
                        f"`{qualified_name}`: `{name}`",
                    ]))
                else:
                    name = name[0]
                if name in types:
                    raise KeyError(' '.join([
                        'Duplicate parameter type for object',
                        f'`{qualified_name}`: `{name}`',
                    ]))

                # TODO support dataclass format: param = default -> type
                type_str = field.children[1].astext()
                parsed_types = self.re_typedoc.findall(type_str)

                num_parsed_types = len(parsed_types)
                if num_parsed_types < 1:
                    raise ValueError(' '.join([
                        'No type found in parsing the object',
                        f"{qualified_name}'s type param {name}: {type_str}",
                    ]))

                if parsed_types[-1][1]:
                    default = self._get_object(obj, parsed_types[-1][1])
                else:
                    default = ValueExists.false

                # Store docstring linking for this argument's ArgDoc
                if parsed_types[0][0] == 'see':
                    if num_parsed_types == 2:
                        doc_linking[name] = (parsed_types[1][0], None)
                    elif num_parsed_types == 3:
                        doc_linking[name] = (
                            parsed_types[1][0],
                            parsed_types[2][0],
                        )
                    elif num_parsed_types > 3:
                        raise ValueError(' '.join([
                            'More than 3 elements for doc linking found in',
                            f"object `{qualified_name}`'s param",
                            f': {type_str}',
                        ]))
                    continue # TODO handle dups/missing type/param check

                found_types = []
                for found, _ in parsed_types:
                    found_types.append(self._get_object(obj, found))

                if len(found_types) > 1:
                    found_types = MultiType(found_types)
                else:
                    found_types = found_types[0]

                    if self.whitelist:
                        #if found_types is None:
                        #    recursive_parse[name] = found_types
                        #else:
                        try:
                            ft_qname = get_full_qual_name(found_types)
                        except Exception as e:
                            raise ValueError(' '.join([
                                '`found_types` has unexpected value',
                                f'`{found_types}` for attribute `{name}`',
                            ])) from e
                        if ft_qname in self.whitelist:
                            recursive_parse[name] = found_types

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
                        raise ValueError(' '.join([
                            'Multiple `returns` fields exist in object',
                            f'`{qualified_name}`',
                        ]))
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
                        raise ValueError(' '.join([
                            'Multiple `rtype` fields exist in object',
                            f'`{qualified_name}`',
                        ]))
                    # TODO Namespace grabbing of types... not just store str
                    returns.type = self._get_object(
                        obj,
                        field.children[1].astext(),
                    )
                else:
                    # TODO Namespace grabbing of types... not just store str
                    returns = BaseDoc(
                        '',
                        self._get_object(obj, field.children[1].astext()),
                    )

        # Specific arg doc linking within an object's __doc__
        self.parse_recursive_see_specific(
            recursive_parse,
            doc_linking,
            qualified_name,
            params,
            types,
            parent,
            recursion_limit,
        )

        # Doc linking via see all meaning: see all args/attirbutes from object
        params = self.parse_recursive_see_all(
            obj,
            qualified_name,
            params,
            types,
            see_args_count,
            parent,
            recursion_limit,
        )

        # Any unmatched pairs of params and types raises an error
        if xor_set := set(types) ^ set(params):
            raise ValueError(' '.join([
                'Unmatched params and types in the docstring of object',
                f'{qualified_name}: {xor_set}'
            ]))

        if not params:
            params = None
        return description, params, returns

    def parse_func(self, obj, recursion_limit=0, parent=None):
        description, args, returns = self.parse_desc_args_returns(
            obj,
            recursion_limit=recursion_limit,
            parent=parent,
        )
        # Return the Function Docstring Object that stores the docsting info
        return FuncDocstring(
            obj,
            description,
            args=args,
            returns=returns,
        )

    def parse_class(
        self,
        obj,
        methods=None,
        recursion_limit=0,
        parse_init=True,
    ):
        """Parse the given class, obtaining its attributes and given functions.

        Args
        ----
        obj : object
            The class object whose docstring and whose methods' docstrings are
            to be parsed.
        methods : [str] = None
            Additional methods whose docstrings are to be parsed.
        """
        # Parse description and attributes, ignoring returns, unless functional?
        description, args, returns = self.parse_desc_args_returns(obj)

        # Obtain the class' __init__ docstring
        # TODO Beware if this qname does not match.
        qname = get_full_qual_name(obj)

        if parse_init:
            if is_dataclass(obj) and isclass(obj):
                # obj is a dataclass subclass, use docstring from __post_init__
                init_obj = getattr(obj, '__post_init__')
                init_qname = f'{qname}.__post_init__'
            else:
                init_obj = getattr(obj, '__init__')
                init_qname = f'{qname}.__init__'
            if init_qname in self.parsed_tokens:
                init = self.parsed_tokens[init_qname]
            elif duck_test_issubclass_namedtuple(obj):
                # If a namedtuple duck type, then __init__ is none, & use attrs
                init = None
            else:
                if not init_obj.__doc__:
                    # TODO if __init__ does not have a docstring or no args but
                    # Attributes does and the attribute names match the init's
                    # arg names, then simply use the attribute docstrings as
                    # the args, assuming it is like a dataclass w/ generated
                    # init.

                    # TODO Related, allow for only partially defined args if
                    # the others are like dataclass values (when actually a
                    # dataclass, able to be checked. This check could include
                    # if the arg is used to assign to the attribute without any
                    # change to its value (attrib = arg).
                    raise NotImplementedError(
                        #logging.warning(
                        'init w/o docstrings are not supported yet. %s',
                        init_qname
                    )
                else:
                    init = self.parse_func(
                        init_obj,
                        recursion_limit=recursion_limit + 1,
                        parent=args,
                    )
                    self.parsed_tokens[init_qname] = init
        else:
            init = ValueExists.false

        # Parse all given method docstrings
        if methods:
            method_docstrs = {}
            for method in methods:
                if not hasattr(obj, method):
                    raise KeyError(
                        f'`obj` `{obj}` does not have method {method}'
                    )

                method_obj = getattr(obj, method)
                if not callable(method_obj):
                    raise TypeError(
                        f'`{obj}.{method}` is not callable: {method_obj}`'
                    )

                method_docstrs[method] = self.parse_func(
                    method_obj,
                    recursion_limit=recursion_limit + 1,
                    parent=args,
                )
                # TODO add qname and object to self.parsed_tokens
        else:
            method_docstrs = None

        parsed_class = ClassDocstring(
            obj,
            description,
            attributes=args,
            init=init,
            methods=method_docstrs,
        )

        if init is None:
            parsed_class.init = FuncDocstring(
                obj.__init__,
                description,
                args=args,
                returns=ValueExists.false,
            )

        return parsed_class

    def parse(
        self,
        obj,
        name=None,
        obj_type=None,
        methods=None,
        style=None,
        recursion_limit=0,
    ):
        """General parsing of a given object with a __doc__ attribute or a
        configuration file.

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
        if recursion_limit > self.recursion_limit:
            raise ValueError(' '.join([
                'Over maximum depth of doc linking function calls:',
                f'{recursion_limit}/{self.recursion_limit}',
            ]))

        # TODO optionally parallelize the parsing, perhaps with Ray or asyncio?
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
                f'parameters given. Recieved `obj` of type: `{type(obj)}`',
            ]))

        # TODO this is recursive, so will call everytime up the chain, probably
        # not desired. This is tmp hot informative fix till every error has the
        # full qual name within it, thuse making these redundant and
        # uninformative.
        if isinstance(obj, FunctionType):
            # TODO this is recursive, so will call everytime up the chain,
            # probably not desired.
            parsed_token = self.parse_func(obj)
            self.parsed_tokens[parsed_token.full_qual_name] = parsed_token
            return parsed_token

        # elif isinstance(obj_type, type): TODO raise if not class object?
        # TODO handle detection of methods, have option ot find those with
        # docs, warn when encountering those without docs.
        #return self.parse_class(obj, name, obj_type)

        # TODO this is recursive, so will call everytime up the chain, probably
        # not desired. This is tmp hot informative fix till every error has the
        # full qual name within it, thuse making these redundant and
        # uninformative.
        parsed_token = self.parse_class(obj)
        self.parsed_tokens[parsed_token.full_qual_name] = parsed_token
        return parsed_token


def parse_config(docstr_args, prog_args):
    """Handles the config parsing before passing to docstr.parse()"""
    # TODO load docstr config and tree to be parsed.
    """
    if isinstance(obj, str) and os.path.splitext(obj)[-1] in {'.yaml', '.ini'}:
        with open(obj, 'r') as openf:
            config = yaml.safe_load(openf)
    elif isinstance(obj, filestream):
        config = yaml.safe_load(obj)
    elif not isinstance(obj, dict):
        raise TypeError(' '.join([
            'Expected, config file path, file stream, or dictionary, but',
            f'recieved: {type(obj)}',
        ]))

    if 'docstr' in config:
        # Obtain the docstr config values, possibly use ConfigArgParse for this
        # Override
        pass
        raise NotImplementedError(' '.join([
            'ConfigArgParse ignores the rest, so make specific parser for',
            'docstr parse/run.',
        ]))
    """

    # TODO Handle all Docstr configuration via cap
    # TODO generate whitelist from the docstr namespace.

    # TODO If given the config files are not accompanied by pre-parsed tokens,
    #   parse the objects within the config starting with the main function and
    #   generate the ConfigArgParser for the specific python program.
    return parse(
        docstr_args.entry_obj,
        style=docstr_args.style,
        whitelist=docstr_args.whitelist,
    )

    # TODO After the CAP for this program is made, use to run the program given
    # config and other arguments not used by the docstr CAP.
    #prog_cap = get_configargparser(tokens)
    #getattr(**prog_cap.parse_args(args.prog_args), docstr_args.main)()


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
