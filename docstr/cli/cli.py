"""The base docstr command line interface through ConfigArgParse."""
from functools import partial
from importlib import import_module
import logging
import os
from operator import attrgetter
import sys
import yaml

import configargparse as cap

from docstr import parse_config #, parse
from docstr.configargparse import (
    NestedNamespace,
    YAMLConfigFileParserCustomLoader,
    add_default_mappings,
    get_configargparser,
    init_prog,
)
from docstr.docstring import get_full_qual_name


# TODO Run ConfigArgParse subparser
def run_cap(subparsers):
    """Given a config file, run the program using docstr, parsing as necessary.
    """
    subcap = subparsers.add_parser(
        'run',
        help='Run a python program given the config file.',
    )

    # TODO I dislike the required -c and --docstr.config instead of positional,
    #   but this seems necessary with ConfigArgParse as it is seems to work.
    subcap.add_argument(
        '-c',
        '--docstr.config',
        required=True,
        #'config',
        is_config_file=True,
        help='The config file of the python program to be run using docstr.',
    )

    subcap.add_argument(
        '-s',
        '--docstr.style',
        required=True,
        help=' '.join([
            'The default docstring style used in the project to be parsed by',
            'docstr.',
        ]),
        #dest='',
    )

    subcap.add_argument(
        '-m',
        '--docstr.main',
        required=True,
        help=' '.join([
            "The python object's name that serves as the main function to",
            'run the python program. This may be a fully qualified name,',
            'which means it is the full module path appeneded with a period',
            'and the qualified name of the object that is the main function.',
            'If the python namespace for docstr is defined, then the aliases',
            'used for the main function may be used. See `from import` and',
            '`import as` commands.',
        ]),
        #dest='docstr.main',
    )

    import_alias_help = ' '.join([
        '**import as**: To alias an object imported from a module,',
        'The "import" entry consists of a dictionary mapping of the actual',
        'object imported to its alias to use in parsing the configuration of',
        'python program, e.g., `import object as obj` is:',
        '\n```',
        '\timport:',
        '\t\tobject: obj',
        '\n```',
    ])

    subcap.add_argument(
        '--docstr.from_import',
        required=False,
        type=dict,
        #dest='docstr.from_import',
        help=' '.join([
            "To specify the equivalent of python's",
            '`from module import object` a dictionary mapping mapped to by',
            '`from import` or `from-import` to a dictionary of module names',
            'that map to a list of objects to be imported from those modules.',
            'For example, for the following python from import snippet:',
            '\n```\n',
            'from module_root.module_child import (',
            '\n\tobject_1',
            '\n\tobject_2',
            '\n)',
            '\n```\n',
            'The equivalent is the following yaml:',
            '\n```\n',
            'from import:',
            '\n\tmodule_root.module_child:',
            '\n\t\t- object_1',
            '\n\t\t- object_2',
            '\n```\n',
            f'\n{import_alias_help}',
            '\n\nUnlike typical python import syntax, the `from-import`',
            'argument supports the same use of `as` for aliasing imported',
            'objects, as in `import object as obj`. The following are',
            'result in an equivalent namespace created. In python:',
            '\n```\n',
            'from module_root.module_child import (',
            '\n\tobject_1',
            '\n\tobject_2',
            '\n)',
            '\nfrom module_root.module_child import object_3 as obj3',
            '\n```\n',
            'The equivalent is the following yaml:',
            '\n```\n',
            'from import:',
            '\n\tmodule_root.module_child:',
            '\n\t\t- object_1',
            '\n\t\t- object_2',
            '\n\t\t- object_3: obj3',
            '\n```\n',
        ]),
    )

    # TODO support basic import
    #subcap.add_argument(
    #    '--import',
    #    required=False,
    #    help=' '.join([
    #        f'\n{import_alias_help}',
    #    ]),
    #)

    """
    subcap.add_argument(
        'prog_args',
        nargs='?',
        type=list,
        help='The remaining arguments to be used by the python program.',
    )
    #"""

    # TODO map a function call to parse_config() when run subcmd used.


# TODO Parse ConfigArgParse subparser
def parse_cap(subparsers):
    """Parse a given list of objects, passing or saving the parsed tokens."""
    raise NotImplementedError()


# TODO Compile ConfigArgParse subparser
def compile_cap(subparsers):
    """Compile actions of docstr given parsed tokens."""
    raise NotImplementedError()


def unknown_tag(loader, suffix, node):
    if isinstance(node, yaml.ScalarNode):
        constructor = loader.__class__.construct_scalar
    elif isinstance(node, yaml.SequenceNode):
        constructor = loader.__class__.construct_sequence
    elif isinstance(node, yaml.MappingNode):
        constructor = loader.__class__.construct_mapping

    data = constructor(loader, node)

    return data


def prototype_hack_reformat_yaml_dict_unnested_cap(config_path):
    if isinstance(config_path, str):
        with open(config_path, 'r') as openf:
            loader = yaml.SafeLoader
            #loader.add_constructor(None, lambda x, y: x.construct_mapping(y,
            #   True))
            #loader.add_multi_constructor('!', unknown_tag)
            #loader.add_multi_constructor(
            #    '', lambda loader, tag_suffix, node: tag_suffix + ' ' +
            #    node.value,
            #)
            config = yaml.load(openf, Loader=loader)
    elif isinstance(config_path, dict):
        config = config_path
    else:
        raise TypeError(f'Unexpected config_path type: {type(config_path)}')

    # TODO parse docstr config & namespace things from docstr part of yaml
    docstr_parsed = {}
    docstr_config = config.pop('docstr') # Crashes if no docstr key
    #reformatted_key = f"docstr.{key.replace(' ', '_')}"

    cap_namespace = NestedNamespace()
    cap_namespace.docstr = NestedNamespace()
    cap_namespace.docstr.style = docstr_config.pop('style', 'numpy')
    cap_namespace.docstr.main = docstr_config.pop('main', None)
    cap_namespace.docstr.configs = docstr_config.pop('configs', None)

    cap_namespace.docstr.log_sink = docstr_config.pop('log_sink', None)
    cap_namespace.docstr.log_level = docstr_config.pop('log_level', None)

    # Accept both ints and str for log level
    if cap_namespace.docstr.log_level is not None:
        try:
            cap_namespace.docstr.log_level = \
                int(cap_namespace.docstr.log_level)
        except ValueError:
            pass

    if len(docstr_config) > 1:
        raise ValueError(
            f'Unexpected more keys, other than from imoprt:\n{docstr_config}'
        )

    key, from_import = docstr_config.popitem()

    if key not in {'from import', 'from_import'}:
        raise ValueError(f'Unexpected key in docstr config: {key}')
    del key

    # Handle namespace things given `from_import`
    namespace = {}
    for module, objs in from_import.items():
        imported_module = import_module(module)
        if isinstance(objs, str):
            namespace[objs] = attrgetter(objs)(imported_module)
        elif isinstance(objs, list):
            for obj in objs: # NOTE does not support `from import as`
                namespace[obj] = attrgetter(obj)(imported_module)
        else:
            raise TypeError(
                f'Unexpected module mapped value type: {type(objs)}'
            )

    # Given the namespace in the config (or not), reformat the config dict into
    # expected nested format.
    config_reformatted = {}

    # Depth first loop that walks the remaining "tree" config.
    first_item = config.popitem()
    item_stack = [first_item[1]]

    # Need to keep track of accepted parents as prefix.
    if first_item[0] in namespace:
        stack_prefix = ''
        entry_obj = first_item[0]
    else:
        stack_prefix = first_item[0]
        if len(first_item[1]) == 1:
            entry_obj = list(first_item[1].keys())[0]
        else:
            raise NotImplementedError('Naming the prog with more than one key')
    cap_namespace.docstr.prog_name = first_item[0]
    setattr(cap_namespace, first_item[0], NestedNamespace())

    # TODO There is some silent and not always occurring bug where 2
    # rpartitions of the stack_prefix occurs.
    #   Seems to be when removing keys that are named values in namespace, it
    #   does not go through all their values as part of that object if there
    #   were others to go through.
    # We could know when NOT to decrement stack_prefix, and that is if the
    # current empty dict is for a dict with only one key to a configurable
    # object,
    # TODO the unit tests need to include this kind of hierarchical test cases

    # This is a hot fix to store if it is a configurable object or a named arg.
    hierarchical_config = [True]

    while item_stack:
        if isinstance(item_stack[-1], dict):
            if item_stack[-1]:
                # is non-leaf w/ children
                next_item = item_stack[-1].popitem()
                if next_item[0] not in namespace:
                    if stack_prefix:
                        stack_prefix += f'.{next_item[0]}'
                    else:
                        stack_prefix = next_item[0]
                    hierarchical_config.append(True)
                else:
                    hierarchical_config.append(False)
                item_stack.append(next_item[1])
            else:
                # the non-leaf is empty, time to pop
                #print('')
                #print(stack_prefix)
                #for item_ya in item_stack:
                #    print(item_ya)
                item_stack.pop()
                if hierarchical_config.pop():
                    stack_prefix = stack_prefix.rpartition('.')[0]
        else: # item is a leaf
            config_reformatted[stack_prefix] = item_stack.pop()
            if hierarchical_config.pop():
                stack_prefix = stack_prefix.rpartition('.')[0]

    cap_namespace.docstr.namespace = namespace
    cap_namespace.docstr.entry_obj = namespace[entry_obj]
    cap_namespace.docstr.whitelist = {
        get_full_qual_name(n) for n in namespace.values()
    }
    getattr(cap_namespace, first_item[0]).args = config_reformatted

    return cap_namespace


def docstr_cap(config=None, known_args=False, return_prog=False):
    """The docstr main ConfigArgParser."""
    if config is None:
        sys_argv = sys.argv
        config = sys_argv[1]

        if len(sys_argv) > 2 :
            prog_args = sys_argv[2:]
        else:
            prog_args = []
    else:
        prog_args = None

    # NOTE Does note need to be a sys_argv, can be a str positional in CAP.
    if isinstance(config, str):
        ext = os.path.splitext(config)[-1]
        if ext != '.yaml':
            raise NotImplementedError(
                'Currently only yaml configs are supported.',
            )

    #logging.debug('Parsing docstr args and reformatting config internally.')
    # Parse the yaml config into the format for docstr prototype w/ CAP
    cap_namespace = prototype_hack_reformat_yaml_dict_unnested_cap(config)

    # Handle configuring root logger
    if isinstance(cap_namespace.docstr.log_level, str):
        log_level = getattr(
            logging,
            cap_namespace.docstr.log_level.upper(),
            None,
        )
    else:
        log_level = cap_namespace.docstr.log_level

    if cap_namespace.docstr.log_sink in {'stderr', 'stdout'}:
        logging.basicConfig(
            stream=getattr(sys, cap_namespace.docstr.log_sink),
            level=log_level,
            format='%(asctime)s; %(levelname)s: %(name)s: %(message)s',
        )
    elif cap_namespace.docstr.log_sink is not None:
        logging.basicConfig(
            filename=cap_namespace.docstr.log_sink,
            level=log_level,
            format='%(asctime)s; %(levelname)s: %(name)s: %(message)s',
        )

    #root_cap = cap.ArgumentParser(
    #    prog='docstr',
    #    description='Python docstring parsing for write once design.',
    #    config_file_parser_class=cap.YAMLConfigFileParser,
    #    # TODO want to be able to support any config file format CAP supports.
    #    default_config_files=['~/.docstr/docstr_defaults'],
    #)

    # TODO Implement docstr CAP (arg group), after prototype

    # TODO Pass the rest of the args via sys_arv to the docstr CAP.


    # TODO implement any necessary subcommands, after prototype hack
    #subcaps = root_cap.add_subparsers(help='subcommand help',)
    #run_cap(subcaps)
    #parse_cap(subcaps)
    #compile_cap(subcaps)

    logger = logging.getLogger(__name__)
    logger.debug('Parsing program docstrings.')

    # TODO pass the docstr cap to the parse_config() or parse()
    #   We want docstr cap to handle config path, given file stream, & dict.
    #parse_config(*root_cap.parse_known_args(namespace=NestedNamespace()))
    tokens = parse_config(
        cap_namespace.docstr,
        getattr(cap_namespace, cap_namespace.docstr.prog_name),
    )

    # Create docstr yaml SafeLoader with yaml tags for mapping defaults.
    if cap_namespace.docstr.configs:
        loader = add_default_mappings(
            yaml.SafeLoader,
            cap_namespace.docstr.configs,
        )
        loader = partial(YAMLConfigFileParserCustomLoader, loader=loader)
    else:
        loader = 'yaml'

    logger.debug('Generating ConfigArgParser for program.')
    # TODO parsing of docstrings finished, get the CAP form those tokens
    prog_cap = get_configargparser(tokens, config_file_parser=loader)

    # TODO run the program with the parsed tokens and aligned CAP values
    #getattr(**prog_cap.parse_args(args.prog_args), docstr_args.main)()

    logger.debug('Parsing program arguments.')
    if known_args:
        args = prog_cap.parse_known_args(
            args=prog_args,
            namespace=NestedNamespace(),
            config_file_contents=yaml.dump(
                getattr(cap_namespace, cap_namespace.docstr.prog_name).args
            ),
        )[0]
    else:
        args = prog_cap.parse_args(
            args=prog_args,
            namespace=NestedNamespace(),
            config_file_contents=yaml.dump(
                getattr(cap_namespace, cap_namespace.docstr.prog_name).args
            ),
        )
    #setattr(cap_namespace, cap_namespace.docstr.prog_name, args)

    logger.debug('Beginning to initialize program.')
    prog_ready = init_prog(args)


    if return_prog:
        logger.debug('Program is ready. Now returning.\n=====')
        return prog_ready
    logger.debug('Program is ready. Now running.\n=====')

    # Based on cap_namespace.docstr main and entry_obj, run the init prog.
    if cap_namespace.docstr.main == cap_namespace.docstr.entry_obj.__name__:
        logger.warning(
            'Entry object was run during init. :/ '
            'This needs fixed after prototype.'
        )
        return
        # Then it is a callable object to be run
        #return prog_ready()


    # Is a class with main being a method on it to be called to run
    return getattr(prog_ready, cap_namespace.docstr.main)()


if __name__ == '__main__':
    results = docstr_cap()
