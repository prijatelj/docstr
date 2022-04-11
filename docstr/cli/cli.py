"""The base docstr command line interface through ConfigArgParse."""
import configargparse as cap

from docstr import parse_config #, parse
from docstr.configargparse import NestedNamespace

# TODO Run ConfigArgParse subparser
def run_cap(subparsers):
    """Given a config file, run the program using docstr, parsing as necessary.
    """
    subcap = subparsers.add_parser(
        'run',
        help='Run a python program given the config file.',
    )
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

def docstr_cap():
    """The docstr main ConfigArgParser."""
    root_cap = cap.ArgumentParser(
        prog='docstr',
        description='Python docstring parsing for write once design.',
        config_file_parser_class=cap.YAMLConfigFileParser,
        default_config_files=['~/.docstr/docstr_defaults'],
    )
    # TODO want to be able to support any config file format CAP supports.

    subcaps = root_cap.add_subparsers(help='sub-command help',)
    run_cap(subcaps)
    #parse_cap(subcaps)
    #compile_cap(subcaps)

    # TODO pass the docstr cap to the parse_config() or parse()
    #   We want docstr cap to handle config path, given file stream, & dict.
    parse_config(*root_cap.parse_known_args(namespace=NestedNamespace()))

if __name__ == '__main__':
    docstr_cap()
