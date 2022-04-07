from collections.abc import Callable

import configargparser as cap

from docstr.docstrings import MultiType

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
    cli = cap.ArgumentParser(
        prog='NumpyDocClassRecursiveParse',
        description='A class with objects to be parsed.',
    )

    # TODO Create a sub/hierarchical ConfigArgParser
    #sub_cli = cli.add_argument_group(
    sub_cli = cap.ArgumentParser(
        prog='NumpyDocClass',
        description="""This is an example class with Numpy docstrings. Short description ends. This is the beginning of the long descriptions, which can essentially be arbitrary text until the next section/field occurs.\n# TODO include MathTex/LaTeX math here to ensure parsing works with it. I don't think I can use the $ character to delimit docstr linking as MathTex may use it! So I need to ensure the character I use is commonly NOT used by other things wrt docstrings. Perhaps I could just use the markdown for hyperlinking, but use some indication of namespace / within code linking.\n# TODO Include example of hyperlinking in long description""",
    )

    # TODO If possible, rather than having to chain `dest` params with the
    # NestedNamespace's path from root cli to this cli appeneded by dots '.', I
    # want to be able to access nested args through contexts, meaning, to get
    # to this sub_cli, in the cli, I could write --cli `--name 'Name' ...` and
    # chain more args that way within the context of going to this sub_cli
    sub_cli.add_argument(
        'name',
        help='The name associated with the object instance.',
        dest='very_useful_class.name', # NOTE tmp; to be automated & unneeded
    )
    sub_cli.add_argument(
        'a',
        type=MultiType({int, float}),
        help='First number in summation.',
        dest='very_useful_class.a', # NOTE tmp; to be automated & unneeded
    )
    sub_cli.add_argument(
        'b',
        type=MultiType({int, float}),
        help='Second number in summation.',
        dest='very_useful_class.b', # NOTE tmp; to be automated & unneeded
    )
    sub_cli.add_argument(
        '-x',
        '--x',
        type=MultiType({int, float}),
        default=8,
        help='First number in multiplication.',
        dest='very_useful_class.x', # NOTE tmp; to be automated & unneeded
    )
    sub_cli.add_argument(
        '-y',
        '--y',
        type=MultiType({int, float}),
        default=11,
        help='Second number in multiplication. This is an example of alternative specification of default. This support is included in order to be more inclusive of pre-existing standards used by others so that docstr could be applied to these cases. Docstr is intended to allow modifcation to their parsing regexes such that custom support for niche user cases may be handled by the user.',
        dest='very_useful_class.y', # NOTE tmp; to be automated & unneeded
    )
    sub_cli.add_argument(
        '-z',
        '--z',
        type=float,
        default=3.14159,
        help='An example of an attribute with a default value, typically set in init.',
        dest='very_useful_class.z', # NOTE tmp; to be automated
    )

    # TODO add the sub/hierarchical ConfigArgParser as an argument
    cli.add_nested_parser(
        'very_useful_class',
        'Truly, a very useful class instance.',
        sub_cli,
    )

    # TODO add a function/Callable argument
    cli.add_argument(
        'func_2',
        type=Callable, # TODO handle get function from str
        default=examples.func_defaults,
        description="A function to be called throughout the class' use."
    )

    return cap


if __name__ == '__main__':
    cli = make_cli()
    cli.parse_args()
