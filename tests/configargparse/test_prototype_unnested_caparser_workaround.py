"""This test check the conversion of a yaml dict into the prototype version's
NestedNamespace format for docstr's internal ConfigArgParsers (CAP). This is
only a workaround and will be replaced in future versions where there will be
an extention to the configargparser.ArgumentParser to support Nested args and
configs as desired by docstr intended use cases.
"""
import yaml

import pytest

from docstr.cli import cli
from docstr.configargparse import NestedNamespace
from docstr.parsing import parse_config

import tests.numpy_example_docstrings as examples
from tests.example_configargparser import make_cli


@pytest.mark.dependency(name='prototype_conversion')
def test_prototype_yaml_dict_nested_conversion():
    namespace = cli.prototype_hack_reformat_yaml_dict_unnested_cap(
        'tests/numpy_example_config.yaml'
    )

    # Check the entry object name is correct. This is the python program name.
    assert namespace.docstr.entry_obj == examples.NumpyDocClassRecursiveParse

    # prog_name is based on the top level key of the yaml config.
    assert namespace.docstr.prog_name == 'NumpyDocClassRecursiveParse'

    # Check the resulting docstr config
    assert isinstance(namespace, NestedNamespace)
    assert isinstance(namespace.docstr, NestedNamespace)
    assert namespace.docstr.style == 'numpy'
    assert namespace.docstr.main == 'run'
    assert namespace.docstr.whitelist == {
        'tests.numpy_example_docstrings.func_choices',
        'tests.numpy_example_docstrings.NumpyDocClass',
        'tests.numpy_example_docstrings.NumpyDocClassRecursiveParse',
    }
    assert namespace.docstr.namespace == {
        'func_choices': examples.func_choices,
        'NumpyDocClass': examples.NumpyDocClass,
        'NumpyDocClassRecursiveParse': examples.NumpyDocClassRecursiveParse,
    }

    with open('tests/tmp_config.yaml', 'r') as openf:
        expected_config = yaml.safe_load(openf)

    # Should be the converted pseudo-nested dict format
    reformatted = getattr(namespace, namespace.docstr.prog_name).args
    print('reformatted:\n', reformatted)
    print('expected config:\n', expected_config)
    assert reformatted == expected_config

# TODO test the generated configargparse.ArgParser w/ NestedNamespace.
#   TODO this involves implementing choices in cap generation
#       MultiType: Make it a container of its types to support.
#   TODO As well as str of namespace object conversion into the actual object.
#       any single type and MultiType: Make it (optionally) check if it can
#       convert given the docstr namespace and "global module" context.

@pytest.mark.dependency(depends=['prototype_conversion'])
#@pytest.mark.xfail
def test_generate_configargparser():
    example_cli = make_cli()
    #example_args = example_cli.parse_args(namespace=NestedNamesace())

    namespace = cli.prototype_hack_reformat_yaml_dict_unnested_cap(
        'tests/numpy_example_config.yaml'
    )

    tokens = parse_config(
        namespace.docstr,
        getattr(namespace, namespace.docstr.prog_name),
    )

    prog_cap = cli.get_configargparser(tokens)

    # Unable to compare ArgumentParsers w/ `==`??? So compare parsed args
    assert prog_cap == example_cli

# TODO must be able to pass the converted yaml dict to
#   configargparse.ArgumentParser.parse_args(), or somehow have same
#   functionality.

# TODO test running of configargparse.ArgParser w/ NestedNamespace w/ tokens
#   Simply, the output will be func_2 defaults, by config as is, that's
#   func_choices' defaults.
