"""This test check the conversion of a yaml dict into the prototype version's
NestedNamespace format for docstr's internal ConfigArgParsers (CAP). This is
only a workaround and will be replaced in future versions where there will be
an extention to the configargparser.ArgumentParser to support Nested args and
configs as desired by docstr intended use cases.
"""
import yaml

from docstr.cli import cli
from docstr.configargparse import NestedNamespace
import tests.numpy_example_docstrings as examples

def test_prototype_yaml_dict_nested_conversion():
    prog_name, namespace = cli.prototype_hack_reformat_yaml_dict_unnested_cap(
        'tests/numpy_example_config.yaml'
    )

    # Check the entry object name is correct. This is the python program name.
    assert prog_name == 'NumpyDocClassRecursiveParse'

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
    reformatted = getattr(namespace, prog_name).args
    print('reformatted:\n', reformatted)
    print('expected config:\n', expected_config)
    assert reformatted == expected_config

# TODO test the generated configargparse.ArgParser w/ NestedNamespace.
#   TODO this involves implementing choices in cap generation
#       MultiType: Make it a container of its types to support.
#   TODO As well as str of namespace object conversion into the actual object.
#       any single type and MultiType: Make it (optionally) check if it can
#       convert given the docstr namespace and "global module" context.

# TODO test running of configargparse.ArgParser w/ NestedNamespace w/ tokens
#   Simply, the output will be func_2 defaults, by config as is, that's
#   func_choices' defaults.
