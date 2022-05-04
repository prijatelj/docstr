"""ConfigArgParse specific extentions or utils for docstr."""
from collections import OrderedDict
from functools import partial
import yaml

import configargparse as cap

from docstr.docstring import (
    ValueExists,
    MultiType,
    Docstring,
    ClassDocstring,
    FuncDocstring,
)
# TODO should handle Callable, etcs in parsing the tokens?
#from docstr.parsing import get_namespace_obj, get_module_object


# TODO Nested ConfigArgParse Namespace and a parser module to be nested.
#   extend argparse's argument groups to be their own CAP parser module.
#   Consider: `ArgumentParser.add_nested_parser(title, description, parser)`
#       returns None
#   OR: `ArgumentParser.add_nested_parser(title, description, prog, nested_desc)`
#       returns ArgumentParser # the nested argument parser.

#   Perhaps, to auto dest set of nested cap module's args, when adding a cap
#   module to another as an argument, in that funciton, modify all dests
#   through breadth first traversal/if all dests accessible just add prefix.
#   OR, rather than any mods, just make them read as if w/ prefix when accessed
#   at some parent cap parser.

# TODO currently NestedNamespace still requires all args to be uniquely
# identified. There is perhaps a better solution that is akin to subparsers,
# but allows for multiple "subparsers" to be called per script call and to
# allow for the subparsers to have overlapping arg names because they are
# inherently nested.


class ArgumentParser(cap.ArgumentParser):
    """An extention to the [config]argparser.ArgumentParser to support nesting
    ArgumentParsers.

    Attributes
    ----------
    see cap.ArgumentParser
    nested_parsers :
        Nested parsers are subparsers that ...

    Notes
    -----
    This should be tested similarly to ConfigArgParse.ArgumentParser by testing
    as a drop in replacement to argparse.ArgumentParser, to ensure the added
    functionality does not hinder any pre-existing expectations or funcitons.
    """
    def __init__(self, *args, **kwargs):
        self._nested_parsers = None
        super().__init__(*args, **kwargs)

    #def add_nested_group(self, title, object_name, description):

    def add_nested_parsers(self, **kwargs):
        """ Cannot be too similar to add subparsers due to needing NOT mutual
        exculsivity.

        This method functions similarly to `add_subparsers()`, except that any
        required argmuments within the nested parsers are also required by the
        parent parser. This allows the nested parsers to operate as a subparser
        does, independently of the parent, as well as extend the parent parser
        to group required arguments as add_argument_group does. The nested
        arguments are accessed by the name of the nested_parser from the parent
        argument parser.

        Returns
        -------
        None | ArgumentParser | ArgumentParserGroup
        """
        raise NotImplementedError("""
            The ideal would be that we do not have to always access the setting
            of an argument using `--nested_1.nested_2.nested_3.nested_3_arg
            VALUE`. And rather could have a nice indentation (if indented over
            multiple lines) and have something like:
            ```
            python argparserino
            ```
        """)
        if self._nested_parsers is not None:
            self.error(_('cannot have multiple nested parser arguments'))

        # Add the parser class to the arguments if it's not present
        kwargs.setdefault('parser_class', type(self))

        # TODO perhaps keep nested parsers under subparsers, but include set of
        # ids or dict of name to the subparsers that are nested parsers? want
        # to preserve subparser functionality entirely and only add more to it.
        if 'title' in kwargs or 'description' in kwargs:
            title = _(kwargs.pop('title', 'nested command groups'))
            description = _(kwargs.pop('description', None))
            self._nested_parsers = self.add_argument_group(title, description)
        else:
            self._subparsers = self._positionals

        # TODO prog defaults to the usage message of this parser, skipping
        # optional arguments and with no "usage:" prefix
        if kwargs.get('prog') is None:
            formatter = self._get_formatter()
            positionals = self._get_positional_actions()
            groups = self._mutually_exclusive_groups
            formatter.add_usage(self.usage, positionals, groups, '')
            kwargs['prog'] = formatter.format_help().strip()

        # TODO create the parsers action and add it to the positionals list
        parsers_class = self._pop_action_class(kwargs, 'parsers')
        action = parsers_class(option_strings=[], **kwargs)
        self._subparsers._add_action(action)

        # Return the created parsers action
        return action


class NestedNamespace(cap.Namespace):
    """An extension to argparse.Namespace allowing for nesting of namespaces.

    Notes
    -----
    Modified version of hpaulj's answer at
        https://stackoverflow.com/a/18709860/6557057

    Use by specifying the full `dest` parameter when adding the arg. then pass
    the NestedNamespace as the `namespace` to be used by `parser.parse_args()`.
    """
    def __setattr__(self, name, value):
        if '.' in name:
            group, _, name = name.partition('.')
            namespace = getattr(self, group, NestedNamespace())
            setattr(namespace, name, value)
            self.__dict__[group] = namespace
        else:
            self.__dict__[name] = value

    def __getattr__(self, name):
        if '.' in name:
            group, _, name = name.partition('.')

            try:
                namespace = self.__dict__[group]
            except KeyError:
                raise AttributeError

            return getattr(namespace, name)
        else:
            getattr(super(NestedNamespace, self), name)

    def pre_init(self):
        """This readies the NestedNamespace for initialization in run().

        With `docstr_type` as a constant/default arg, not required, set to
        default to the object the rest of the args are for in this namespace
        this will create the actual object.

        Note
        ----
        All that is left is figurin out how to start from the leaves of the CAP
        and init down to root, or entry_object.
        """
        pre_nn = NestedNamespace()

        # tmp placeholder for the current nested arg name being initialized.
        pre_nn.docstr_waiting_arg = None
        pre_nn.docstr_args = dict()
        pre_nn.docstr_nested_args = dict()

        args = vars(self)
        for key, val in args.items():
            if key == 'docstr_type':
                pre_nn.docstr_type = val
            elif isinstance(val, NestedNamespace):
                pre_nn.docstr_nested_args[key] = val
            else:
                pre_nn.docstr_args[key] = val
        return pre_nn


# TODO str conversion into objects of expected types
#   This is already supported for "common built-in types and functions".
#   TODO get object from a string of the fully qualified name in python.
#   TODO get the object from the string of relative to the docstr cli's object's module.


# TODO Argument multiple accepted types matching docstr.docstrings.MultiType


# TODO Argument requirement dependency on values of other args.


# TODO Perhaps, find/make a nice formatter_class for customized help output?


def recursive_dict_update(dest, src, copy=True):
    """Updates all dictionaries within a dictionary given a dict of dicts.

    Args
    ----
    dest : dict
        The dictionary to be updated.
    src : dict
        The dictionary used to update the destination dictionary.

    Returns
    -------
    dict
        The resulting destination dictionary updated by the source dictionary.

    Note
    ----
    If an element is a list of dictionaries, a TODO for another function is to
    support extending the existing list if in dest XOR updating the list's
    values that are dicts based on position. In this function, neither of those
    are performed. Here the update only looks for dicts to update, and thus
    will override keys whose values are lists.
    """
    if copy:
        dest = dest.copy()
        src = src.copy()

    # Key: value pairs only in src, then add those w/ values to update
    update = {key: src[key] for key in src.keys() - dest.keys()}
    same_keys_dict_val = set()
    # TODO could get key sets in one pass.
    for key in dest.keys() & src.keys():
        if isinstance(src[key], dict) and isinstance(dest[key], dict):
            same_keys_dict_val.add(key)
        else:
            update[key] = src[key]

    dest.update(update)

    for key in same_keys_dict_val:
        if copy:
            dest[key] = recursive_dict_update(dest[key], src[key], True)
        else:
            recursive_dict_update(dest[key], src[key], False)

    if copy:
        return dest


def default_mapping_constructor(
    loader: yaml.SafeLoader,
    node: yaml.nodes.MappingNode,
    default_map: dict
) -> dict:
    return recursive_dict_update(
        default_map,
        loader.construct_mapping(node, True),
        copy=True,
    )


def add_default_mappings(loader, configs):
    for key, value in configs.items():
        loader.add_constructor(
            f'!docstr.configs:{key}',
            partial(default_mapping_constructor, default_map=value),
        )
    return loader


class YAMLConfigFileParserCustomLoader(cap.YAMLConfigFileParser):
    """YAMLConfigFileParser with a given PyYAML loader.
    Same as YAMLConfigFileParser excepts adds an attribute: loader for a PyYAML
    custom loader to support things like adding constructors to handle custom
    tags, and then uses that loader in parsing.

    Attributes
    ----------
    see YAMLConfigFileParser
    loader : yaml.SafeLoader

    """
    def __init__(self, loader=None, *args, **kwargs):
        super().__init__(*args, **kwargs)
        if loader is None or issubclass(
            loader,
            (yaml.SafeLoader, yaml.CSafeLoader),
        ):
            self.loader = loader
        else:
            raise TypeError(' '.join([
                '`loader` must be a yaml.SafeLoader or yaml.CSafeLoader, for',
                f'safety reasons. Not {type(loader)}',
            ]))

    def parse(self, stream):
        # see ConfigFileParser.parse docstring
        yaml = self._load_yaml()

        try:
            parsed_obj = yaml.load(stream, Loader=self.loader)
        except Exception as e:
            raise cap.ConfigFileParserException(
                "Couldn't parse config file: %s" % e
            )

        if not isinstance(parsed_obj, dict):
            raise cap.ConfigFileParserException(
                "The config file doesn't appear to "
                "contain 'key: value' pairs (aka. a YAML mapping). "
                "yaml.load('%s') returned type '%s' instead of 'dict'." % (
                getattr(stream, 'name', 'stream'),  type(parsed_obj).__name__))

        result = OrderedDict()
        for key, value in parsed_obj.items():
            if isinstance(value, list):
                result[key] = value
            elif value is None:
                pass
            else:
                result[key] = str(value)

        return result

def cast_bool_str(obj):
    if isinstance(obj, bool):
        return obj
    if isinstance(obj, str):
        if obj == 'True':
            return True
        if obj == 'False':
            return False
        else:
            raise ValueError(
                "Docstr ConfigArgParse given str expects values 'True' xor "
                f"'False', but was given: `{obj}`"
            )
    raise ValueError(
        'Docstr ConfigArgParse expected arg to be of type bool or str, where '
        "when a str the values of 'True' xor 'False' are expected, but was "
        f'given type: `{type(obj)}`'
    )


def get_configargparser(
    docstring,
    nested_prefix='',
    parser=None,
    nested_positionals=False,
    config_file_parser='yaml',
):
    """Creates the ConfigArgParser from contents in the given docstr.Docstring.

    Args
    ----
    docstring : ClassDocstring | FuncDocstring
        The root of some tree of docstr parsed tokens to be walked through
        to generate the ConfigArgParser for those parsed tokens.
    parser : ArgParser | argparse._ArgumentGroup = None
        A pre-existing parser object to be extended with a parser for this
        ClassDocstring's configurable initialization arguments.
    neted_positionals : bool = False
        If True, then the nested parser created here and below through
        recursive calling will allow positional arguments for required
        arguments instead of keyword required arguments. The default is
        False, meaning any required argument is made as a required keyword
        argument, non-positional.

    Returns
    -------
    configargparse.ArgumentParser | argparse._ArgumentGroup
    """
    # Type checking of docstring and setting up: args, description, etc.
    if isinstance(docstring, ClassDocstring):
        description = docstring.description
            #f'{docstring.description}\n __init__: \n{docstring.init.description}'
        # TODO store the object in type to recreate the object post CAP parse
        if docstring.init is None or docstring.init.args is None:
            # This is a type of class w/o an init method, thus uses attributes.
            args = docstring.attributes
        else:
            args = docstring.init.args
    elif isinstance(docstring, FuncDocstring):
        description = docstring.description
        # TODO store the object in type to recreate the object post CAP parse
        args = docstring.args
    elif isinstance(docstring, Docstring):
        raise TypeError(' '.join([
            '`docstring` is an unsupported subclass of `docstr.Docstring`.',
            f'Expected ClassDocstring or FuncDocstring, not: {type(docstring)}'
        ]))
    else:
        raise TypeError(f'Unexpected `docstring` type: {type(docstring)}')

    # Setup the nested parser / argument_group
    if parser is None:
        if config_file_parser == 'yaml':
            config_file_parser = cap.YAMLConfigFileParser
        elif config_file_parser == 'ini':
            config_file_parser = cap.ConfigparserConfigFileParser
        elif not isinstance(config_file_parser, partial):
            raise ValueError(
                f'Unexpected `config_file` value: {config_file_parser}'
            )
        nested_parser = cap.ArgumentParser(
            prog=docstring.name,
            description=description,
            config_file_parser_class=config_file_parser,
        )
    elif isinstance(parser, (cap.ArgParser, cap.argparse._ArgumentGroup)):
        # Create the subparsers and pass that down any recursive get_cap()
        # TODO Once a Nested Parser is supported, replace this w/ that
        # This should never occur if docstr cli is used, as that makes
        # the base parser, which already added subparsers

        # TODO handle name prefix for nesting!
        nested_parser = parser.add_argument_group(
            f'{nested_prefix}.{docstring.name}', # TODO WIP! finish this prefix!
            description,
        )
    else:
        raise TypeError(f'Unexpected `parser` type: {type(parser)}')

    nested_parser.add_argument(
        f'--{nested_prefix}.docstr_type' if nested_prefix else '--docstr_type',
        type=type,
        help='docstr internal argument to enable NestedNamespace.init()',
        default=docstring.type,
    )

    # TODO If any Class/FuncDocstring classes in type: recursive call get_cap()
    recursive_args = {}
    for arg_key, arg in args.items():
        if nested_prefix: # TODO this will be handled by the NestedArgumentParser
            name = f'{nested_prefix}.{arg.name}'
        else:
            name = arg.name

        # For `required` and any other args handled similarly by argparse
        arg_kwargs = {}

        if nested_positionals:
            raise NotImplementedError('nested positoinals is not supported.')

        if arg.default is ValueExists.false:
            arg_kwargs['required'] = True

        # TODO handle alias of single letter, perhaps splat expand list?
        #   Seems a list may be given w/o error, so just make name a list.

        default = None if arg.default is ValueExists.false else arg.default
        desc= None if arg.description is ValueExists.false else arg.description

        # TODO handle arg type
        if isinstance(arg.type, (ClassDocstring, FuncDocstring)):
            recursive_args[arg_key] = {
                'name': name,
                'type': arg.type,
                'help': desc,
                'default': default,
            }
            recursive_args[arg_key].update(arg_kwargs)
            continue
        elif isinstance(arg.type, MultiType):
            # TODO consider MultiType allowing recusive config gen

            # TODO consider case when parent class given, but not the actual
            # class that'd need configured. This would be resolved by allowing
            # "live parse" or "JIT compilation" of an object/config given
            # within this arg.

            # choices is if there are only literals in type/MultiType.
            all_literals = all([not isinstance(t, type) for t in arg.type])
            if all_literals:
                arg_kwargs['choices'] = arg.type

        # Handle boolean args' casting as they are a special case.
        if arg.type is bool:
            arg.type = cast_bool_str

        nested_parser.add_argument(
            f'--{name}',
            type=arg.type,
            help=desc,
            default=default,
            **arg_kwargs,
        )

    # TODO this begs for trivial parallelization, possibly async creation
    for rec_args, rec_arg_parts in recursive_args.items():
        get_configargparser(
            rec_arg_parts['type'],
            rec_arg_parts['name'],
            nested_parser,
            nested_positionals,
        )

    return nested_parser


# TODO Either here or docstr/cli make ConfigArgParser for hardware & logging
#   the hardware and logging can inform what parallelization docstr may use, or
#   could be used to inform how to run the python program, possibly. The latter
#   involves solving the issue of communication from docstr to an arbitrary
#   python program. Could just be optoinally used by the python program, so if
#   it can use the configs, then it can if desired.


def init_prog(prog_args):
    """Run the program given parsed tokens and the ConfigArgParser arguments.

    Args
    ----
    tokens : ClassDocstring | FuncDocstring
        The parsed tokens of the python program's docstrings.
    cap_args : NestedNamespace
        The resulting argument values in a nested namespace from running the
        configargparse.ArgumentParser for the python program.
    """
    # TODO Need to initialize the leaves first and work the way down, which
    # involves a depth first traversal to do so if do not have the leaf objects
    # already.

    # When adding to stack, change Namespace into dict of keys: docstr_type,
    # args, nested_args. While nested_args is not an empty list/dict, depth
    # traversal. Once empyty, create the object for that namespace
    cap_stack = [prog_args.pre_init()]
    while cap_stack:
        if cap_stack[-1].docstr_nested_args:
            # cap has next configurable cap in its args (NestedNamespace exist)
            key, val = cap_stack[-1].docstr_nested_args.popitem()
            cap_stack[-1].docstr_waiting_arg = key
            cap_stack.append(val.pre_init())
        else: # current cap is the leaf: last configurable cap
            # Reasign this NestedNamespace to its initialized object
            cap_init = cap_stack.pop()
            if cap_stack:
                cap_stack[-1].docstr_args[cap_stack[-1].docstr_waiting_arg] = \
                    cap_init.docstr_type(**cap_init.docstr_args)
            #else: cap_init is the entry object
    return cap_init.docstr_type(**cap_init.docstr_args)
