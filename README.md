## Docstr : Docstring Parsing for Expedient Programming

The objective of docstr is to make use of properly written docstrings that would be used to create auto-docs through Sphinx and leverage them at runtime to expedite certain programming practices, such as the creation of arg and config parsers, the modular configuration of OOP pipelines, and for leveraging the accurate dpcstrings to reduce text duplication in code.

### Design Principles

- Keep it simple
    - and functional
- Write once
    - reduce redundant code and make it so common code does not need be rewritten for the same functionality.
- Modularity
    - Keep as modular as possible such that each unit may be removed, replaced, or taken and plugged into a different system.
- Efficiency
    - efficient coding and execution

#### Docstr Pipeline Use

1. Give objects whose docstrings are to be parsed
    - pass those objects as args to a function
    - Decorate those objects with a docstr decorator
    - point to those objects via namespace in a configuration file
2. **Parse** the object's docstrings, possibly in a hierarchical fashion if multiple.
    - dependent on docutils and sphinx for conversion of styles to rst
    - uses regex for parsing and tokenizing the docstrings
3. **Tokenize**: The resulting tokens of parsing
    - Syntax check the docstrings to ensure properly written
        - may be done live during the parsing process, or afterwards.
    - Optionally syntax check the docstrings to the objects to ensure they match expectations, e.g., the args in doc are as they are expected by a function.
    - tokenized docstrings enable colorized docstrings in editors.
    - The tokenized objects need to be in a useful enough and general enough format that enables ease of integration into down-stream "compile" software, such as pydantic for type checking, or ConfigArgParse for CLI and config parsers.
4. "**Compile**": Using the tokens, perform operations
    - Command Line Interface: argparse auto creation
    - Configuration file parser: ConfigArgParse auto creation
        - Enables Pipeline running of code if docstr is used on a class that has a run() or main().
            - may hook into or rely upon: Dagster, ray, asyncio
    - Meta-programming (Reflection)
        - enabling type checking versions of the parsed code. (pydantic?)
        - splat extension for "write once".
            If docstr parsed, may automatically generate the boiler plate code based on the parsed docstring, thus reducing writing redundancy.
                - May require linters (pylint, flake8) to acknowledge this.

#### Desired Features for Version 1

The following are desired features for a complete docstr version 1.0.0:

- Auto-generation of an argparser with config support and optional nested namespaces through the parsing of function and class docstrings.
    - functions first
    - classes next
    - linking of docstrings for use in parsing to avoid doc redundancy
    - support of reStructuredText, Google and Numpy styled docstrings
        - support of custom docstring parsers through Sphinx extentions.
    - This is the primary purpose of docstr
- Decorator for specifying the args and kwargs of a function with format as:
    `def func(*args, **kwargs):` to avoid redundant writing of args, defaults, etc.
- Decorator for optional type-checking of variables values at runtime to the
  docstring's preset values.
- Comprehensive unit tests to ensure everything functions as expected.
    - Along with basic CI/CD on github to check build status.
- Hierarchical pipeline support as specified by a yaml config file
    - This allows programmers to focus on OOP design and create their pipelines as modules to be easily sequentially chained or parallelized, and allows the programmer to avoid having to write the boiler plate commonly used in pipelines.
    - This is nearing extra, and programmers would still be able to write the main scripts or call these functions in their own existing programs.
    - End result would be: given a yaml config of a pipeline consisting of python objects in the active namespace who all have parsable docstrings, generate the pipeline running main script with its CLI/configuraiton parser.
- Extra features: features that are unnecessary, but beneficial
    - Parameter iteration and searching (possibly using `pyrameter` or `SHADHO`) to run multiple versions of the same pipeline using different parameters, either
        - This is specifically useful to Machine Learning (ML) researchers, but may be nice for those who either want to exhaustively run variations of their pipeline or have some objective function they want to optimize over different variations of their pipeline.
        - in ML, the pipeline and its parameter search would be entirely contained all in one yaml file, or multiple through optoinal config linking.
            This would result in a straightforward overview of the ML experiment pipeline, easily swapped with existing modules written in code as classes.
    - Possibly rely upon Apache AirFlow DAG for the pipelining.
        - `dag-factory` : AirFlow extension to make dynamic
        - alternative to AirFlow is `dagster`
    - Given an object whose doc string is fully parsed by docstr, output the template of the YAML config file to be editted.

### Verisoning

Docstr uses [Semantic Versioning 2.0.0](https://semver.org/spec/v2.0.0.html).
Docstr's version will remain < 1.0.0 until adequate unit test coverage exists.

### License

The docstr project is licensed under the MIT license by its author Derek S. Prijatelj.
The license is provided in LICENSE.txt
