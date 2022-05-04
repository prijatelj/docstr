from collections.abc import Callable
import yaml

from configargparse import (
    ArgumentParser,
    ConfigparserConfigFileParser,
    YAMLConfigFileParser,
)

from docstr.configargparse import NestedNamespace, cast_bool_str #ArgumentParser
from docstr.docstring import MultiType
from docstr.parsing import get_module_object

import tests.numpy_example_docstrings as examples



def make_cli():
    """Create the ConfigArgParser that matches target NumpyClassRecursiveParse.
    Note that this is not the complete ConfigArgParser if using docstr CLI, but
    rather the subparser that is able to be used through docstr CLI `docstr
    run`.

    This is to be th expected ConfigArgParser from the python call to parse
    ```
    cap = docstr.parse(
        tests.numpy_example_docstrings.NumpyDocClassRecursiveParse,
        'numpy',
        whitelist={'tests.numpy_example_docstrings.NumpyDocClass'},
    ).get_cli(main='NumpyDocClassRecursiveParse.run')
    ```
    """
    cli = ArgumentParser(
        prog='NumpyDocClassRecursiveParse',
        description='A class with objects to be parsed.',
        #\n __init__: \n' + examples.NumpyDocClassRecursiveParse.__init__.__doc__,
        config_file_parser_class=YAMLConfigFileParser,
    )

    #cli.add_argument(
    #    '--config',
    #    #type=yaml.safe_load, # TODO note C Safe loader for yaml.
    #    #required=True,
    #    is_config_file=True,
    #    help="Configuration file path",
    #)

    cli.add_argument(
        '--docstr_type',
        type=type,
        help='docstr internal argument to enable NestedNamespace.init()',
        default=examples.NumpyDocClassRecursiveParse,
    )

    # TODO Create a sub/hierarchical ConfigArgParser
    #nested_parsers = cli.add_nested_parsers()

    sub_cli = cli.add_argument_group(
        'very_useful_class',
        #'NumpyDocClass',
        """NumpyDocClass: This is an example class with Numpy docstrings. Short description ends. This is the beginning of the long descriptions, which can essentially be arbitrary text until the next section/field occurs.\n# TODO include MathTex/LaTeX math here to ensure parsing works with it. I don't think I can use the $ character to delimit docstr linking as MathTex may use it! So I need to ensure the character I use is commonly NOT used by other things wrt docstrings. Perhaps I could just use the markdown for hyperlinking, but use some indication of namespace / within code linking.\n# TODO Include example of hyperlinking in long description""",
    )

    sub_cli.add_argument(
        '--very_useful_class.docstr_type',
        type=type,
        help='docstr internal argument to enable NestedNamespace.init()',
        default=examples.NumpyDocClass,
    )

    # TODO If possible, rather than having to chain `dest` params with the
    # NestedNamespace's path from root cli to this cli appeneded by dots '.', I
    # want to be able to access nested args through contexts, meaning, to get
    # to this sub_cli, in the cli, I could write --cli `--name 'Name' ...` and
    # chain more args that way within the context of going to this sub_cli
    sub_cli.add_argument(
        '--very_useful_class.name',
        help='The name associated with the object instance.',
    )
    sub_cli.add_argument(
        '--very_useful_class.a',
        type=MultiType(frozenset({int, float})),
        help='First number in summation.',
    )
    sub_cli.add_argument(
        '--very_useful_class.b',
        type=MultiType(frozenset({int, float})),
        help='Second number in summation.',
    )
    sub_cli.add_argument(
        '--very_useful_class.x',
        type=MultiType(frozenset({int, float})),
        default=8,
        help='First number in multiplication.',
    )
    sub_cli.add_argument(
        '--very_useful_class.y',
        type=MultiType(frozenset({int, float})),
        default=11,
        help='Second number in multiplication. This is an example of alternative specification of default. This support is included in order to be more inclusive of pre-existing standards used by others so that docstr could be applied to these cases. Docstr is intended to allow modifcation to their parsing regexes such that custom support for niche user cases may be handled by the user.',
    )
    sub_cli.add_argument(
        '--very_useful_class.z',
        type=float,
        default=3.14159,
        help='An example of an attribute with a default value, typically set in init.',
    )

    sub_cli.add_argument(
        '--very_useful_class.ok',
        type=cast_bool_str,
        default=False,
        help="""A bool attribute test for configargparse. There were issues before in
the prototype where any non-empty str input including "False" and
"True" were cast to True, whether in config or cli args.""",
    )

    # TODO add the sub/hierarchical ConfigArgParser as an argument
    #cli.add_nested_parser(
    #    'very_useful_class',
    #    'Truly, a very useful class instance.',
    #    sub_cli,
    #)

    # TODO add a function/Callable argument
    cli.add_argument(
        '--func_2',
        type=get_module_object,
        #type=Callable, # TODO handle get function from str
        # Enable getting from the docstr namespace w/ fallback to global import.
        #type=partial(docstr.parsing.get_namespace_obj(docstr_namespace))
        #type=partial(docstr.parsing.get_module_object) # For full qual names
        default=examples.func_defaults,
        help="A function to be called throughout the class' use."
    )
    return cli


if __name__ == '__main__':
    cli = make_cli()
    args = cli.parse_args(namespace=NestedNamespace())

    print(args)
