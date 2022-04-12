"""The base docstr command line interface through ConfigArgParse."""
from sys import argv as sys_argv
import os
from importlib import import_module
from operator import attrgetter
import yaml

import configargparse as cap

from docstr import parse_config #, parse
from docstr.configargparse import NestedNamespace
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


def prototype_hack_reformat_yaml_dict_unnested_cap(config_path):
    with open(config_path, 'r') as openf:
        config = yaml.safe_load(openf)

    # TODO parse docstr config & namespace things from docstr part of yaml
    docstr_parsed = {}
    docstr_config = config.pop('docstr') # Crashes if no docstr key
    #reformatted_key = f"docstr.{key.replace(' ', '_')}"

    cap_namespace = NestedNamespace()
    cap_namespace.docstr = NestedNamespace()
    cap_namespace.docstr.style = docstr_config.pop('style', 'numpy')
    cap_namespace.docstr.main = docstr_config.pop('main', None)

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
    if first_item[0] in namespace:
        stack_prefix = '' # Need to keep track of accepted parents as prefix.
    else:
        stack_prefix = first_item[0]
    setattr(cap_namespace, first_item[0], NestedNamespace())

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
                item_stack.append(next_item[1])
            else:
                # the non-leaf is empty, time to pop
                item_stack.pop()
                stack_prefix = stack_prefix.rpartition('.')[0]
        else: # item is a leaf
            config_reformatted[stack_prefix] = item_stack.pop()
            stack_prefix = stack_prefix.rpartition('.')[0]

    cap_namespace.docstr.namespace = namespace
    cap_namespace.docstr.whitelist = {
        get_full_qual_name(n) for n in namespace.values()
    }
    getattr(cap_namespace, first_item[0]).args = config_reformatted

    return first_item[0], cap_namespace


def docstr_cap():
    """The docstr main ConfigArgParser."""
    # NOTE Does note need to be a sys_argv, can be a str positional in CAP.
    ext = os.path.splitext(sys_argv[1])[-1]
    if ext != 'yaml':
        raise NotImplementedError('Currently only yaml configs are supported.')

    # Parse the yaml config into the format for docstr prototype w/ CAP
    prog, cap_namespace = prototype_hack_reformat_yaml_dict_unnested_cap(
        sys_argv[1],
    )

    root_cap = cap.ArgumentParser(
        prog='docstr',
        description='Python docstring parsing for write once design.',
        config_file_parser_class=cap.YAMLConfigFileParser,
        default_config_files=['~/.docstr/docstr_defaults'],
    )
    # TODO want to be able to support any config file format CAP supports.

    # TODO Implement docstr CAP (arg group)

    # TODO Pass the rest of the args via sys_arv to the docstr CAP.


    # TODO implement any necessary subcommands, after prototype hack
    #subcaps = root_cap.add_subparsers(help='subcommand help',)
    #run_cap(subcaps)
    #parse_cap(subcaps)
    #compile_cap(subcaps)

    # TODO pass the docstr cap to the parse_config() or parse()
    #   We want docstr cap to handle config path, given file stream, & dict.
    #parse_config(*root_cap.parse_known_args(namespace=NestedNamespace()))
    parse_config(
        cap_namespace.docstr,
        cap_namespace.docstr.namespace[prog],
        getattr(cap_namespace, prog),
    )


if __name__ == '__main__':
    docstr_cap()