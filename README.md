## Docstr : Python Docstring Parsing for Writing Once

Given properly written docstrings that would be used to create auto-docs through Sphinx, `docstr` can use those docstrings at runtime to expedite certain programming practices, such as the creation of argument and config parsers, the modular configuration of piplines of both OOP and funcitonal python components, and reduce code duplication.

| :warning: WARNING! |
|:----------------|
| Any project that is dependent upon the resulting parsed tokens from docstr's parsing of some python object's `__doc__`s will be dependent on the content within the comments of that parsed code! The same applies to any python program that is parsed using the `docstr` CLI. This is by design, as the point is to use the doc strings to write once and reduce redundancy. Future versions may allow work arounds in certain conditions. Future versions will implement more concise and complete error messages similar to that of a compiler for debugging purposes. Support for a 3rd party linter (pylint) will be explored. |

Install docstr from PyPi:

```
pip install docstr
```

This installs the cli tool `docstr`, allowing you to run a python program yaml config with the following line:
```
docstr path/to/a_python_program_config.yaml [arguments for the python program]
```

For examples, please see the `tests/` directory.
There are small Numpy docstring examples of the code with docstrings and the config.yaml.

### Design Principles

1. Write once
    - reduce redundant code and make it so common and similar code does not need to be rewritten for the same functionality.
2. Keep it simple
    - and functional.
3. Modularity
    - Keep as modular as possible such that each unit may be removed, replaced, or taken and plugged into a different system.
4. Efficiency
    - efficient code creation and execution.

#### Docstr Pipeline Use

1. **Load Input** Give objects whose docstrings are to be parsed
    - pass those objects as args to a function
    - Decorate those objects with a docstr decorator
    - point to those objects via namespace in a configuration file
2. **Parse** the object's docstrings, possibly in a hierarchical fashion if multiple.
    - dependent on docutils and sphinx for conversion of styles to rst
    - uses regex for parsing and tokenizing the docstrings
    - **Tokenize**: The resulting tokens of parsing
        - [-TODO-] Syntax check the docstrings to ensure properly written
            - may be done live during the parsing process, or afterwards.
        - [-TODO-] Optionally syntax check the docstrings to the objects to ensure they match expectations, e.g., the args in doc are as they are expected by a function.
        - tokenized docstrings enable colorized docstrings in editors.
        - The tokenized objects need to be in a useful enough and general enough format that enables ease of integration into down-stream "compile" software, such as ([-TODO-]) pydantic for type checking, or ConfigArgParse for CLI and config parsers (done).
        - [-TODO-] Allow for "pre-parsed" docstrings in the case where a docstring is from a 3rd party and is not supported by existing docstr parsing standards.
            In config files, this can be specified in its own section.
3. "**Compile and Run**": Using the tokens, setup and perform operations
    - Command Line Interface: argparse auto creation
    - Configuration file parser: ConfigArgParse auto creation
        - Enables Pipeline running of code if docstr is used on a class that has a run() or main().
            - [-TODO-] may hook into or rely upon: Dagster, ray, asyncio
        - [-TODO-] Decorators may be applied to functions/classes in the config file
            - this may allow for applying Ray to functions/classes.
        - [-TODO-] Allow for configuration files to link to other config files, if so desired.
    - [-TODO-] Meta-programming (Reflection)
        - enabling type checking versions of the parsed code. (pydantic?)
        - splat extension for "write once".
            If docstr parsed, may automatically generate the boiler plate code based on the parsed docstring, thus reducing writing redundancy.
                - May require linters (pylint, flake8) to acknowledge this.
        - docstr.meta.dataclass : make any class a dataclass given correct docstring

### Prototype

The prototype provides the following features, albeit within constrained use cases as it is a prototype.
First is the pipeline followed by the prototype:

1. **Load Input**:
    - When `docstr` is installed, a console script is included.
        Exectuting :
        ```docstr path/to/a_python_program_config.yaml [arguments for the python program]```
        will run the python program based on docstr's parsing of the docstrings and configuration file.
        The prototype will read in the config, adjust docstr's parser settings to that under the `docstr:` options sections.
        Parse the docstrings starting with entry object (the first python object in configuration).
        The parsed docstring tokens will be used to make the ConfigArgParse.ArgumentParser for the python program, and then update the values using the given args and config file.
        The program will then run with those values.
        Look at `docstr/cli/cli.py:docstr_cap()` for the function that the `docstr` command runs.
2. **Parse and Tokenize**
    - Uses sphinx auto doc parsing (relying on docutils too) with napoleaon extention to support Numpy and Google docstring styles.
    - Creates a tree of configurable objects that consists of python classes and functions. Only includes whitelisted objects to be parsed, which is currently inferred from the python namespace imports under the `docstr` section of the yaml config.
    Note that the namespace imports expect these objects to be accessible within the current python environment.
    - supports subclasses of dataclass and NestedTuple, albeit without unit test coverage.
3. **Compile: ConfigArgParse Generation**
    - Generates the ConfigArgParse (CAP) for CLI and configuration creation based on the given python program's yaml file.
    - This is then usable to configure and run the python program through the `docstr` CLI.
    -. **Initialize and Run**
        - initialize the objects from the generated CAP starting from leaves going up to the root of the python program based on the given configuraiton yaml file.
        - Once initialized, the python program will run using the entry object and the given `main` string indicator of what function/method is the main method.

#### Included Specific Features

These are the specific features already included by the prototype, albeit in a limited form.
For all of these specific features, basic unit tests exist.

- Auto-generation of a ConfigArgParser supporting CLI, config files, and env variabels (untested in prototype). The CAP provides a basic nested namespace and carries the configurable object to be instantiated.
    - functions and class methods
    - classes
    - Basic linking of docstrings:
        - recursive linking of the object as an argument of the current one being parsed will be parsed if it is included in the namespace/whitelist of the `docstr.parsing.DocstringParser`.
        - This enables hierarchical pipelines as specified by the given config yaml file.
    - supports reStructuredText, Google and Numpy styled docstrings
        - Support is through Sphinx auto docs w/ napoleaon extenstion.
- (Scuffed but it works for a single program) Hierarchical pipeline support as specified by a yaml config file
    - This allows programmers to focus on OOP design and create their pipelines as modules to be easily sequentially chained or parallelized, and allows the programmer to avoid having to write the boiler plate commonly used in pipelines.
    - This is nearing extra, and programmers would still be able to write the main scripts or call these functions in their own existing programs.
    - End result would be: given a yaml config of a pipeline consisting of python objects in the active namespace who all have parsable docstrings, generate the pipeline running main script with its CLI/configuraiton parser.

### Desired Features Under Development for Version 1.0.0

The following are more desired features for a complete docstr version 1.0.0.
This adds more detail to what is specified in the docstr pipeline section, all of which is expected in version 1.0.0:

0. **General**: [-TODO-]
    - Comprehensive unit tests to ensure everything functions as expected.
        - Along with basic CI/CD on github to check build status.
    - Parallelization and Async support:
        -  Many processes in `docstr` could be parallelized and possibly benefit from async support.
            This is a speed-up option.
1. **Load Input**:
2. **Parse and Tokenize** [-TODO-]
    - further support of parsing the docstrings of dataclasses __post_init__.
        This is crucial.
        - Working in external research code, but unit tests are required here.
    - Need to further test and support the use of the namespace of the module an object is within, including the aliases, so `import pandas as pd` to enable `pd.DataFrame` in that module's docs and same with `import torch; nn = torch.nn`.
    - Some cases where a docstring is either unnecessary or only partially required.
        - by default, complete docs are desired, but in the case where the docs are out of the user's control, support for handling partial docs to run the python program should be supported and be an option able to be specified by the user.
            - docstr configs specific to a set of modules/packages may be beneficial to support.
        - NestedTuple inherting classes don't need to have docstrings beyond adding descriptions to the arguments/attributes, as the rest of the format is exactly the same as if it were to be parsed.
            - (done) NestTuple is explicitly supported through duck typing. Needs unit testing.
            - Are there other such python classes/factories that have typing w/o abc?
    - far more informative exception/error messages from docstr during the parsing process to inform the user exactly what file, line of code, object being parsed, and why it is an error, such as expectations of given context in parsing, and the unexpected thing found.
        - we want the error messages to be informative enough in themselves such that the user does not have to enter a debugger to observe such things a normal compiler, even JIT python, would inform the user of.
    - Need to support in some standard way how to specify that the object
      expected is a specific set of types, as in callable classes, rather than
      instances of those classes.
        - Perhaps Python type hinting has something?
        - for now, `type` as expected parent type of such objects works.
        - perhaps something similar to MultiType but for the class themselves.
            - MultiClass? perhaps not... naming is off.
3. **Compile and Run** [-TODO-]
    - Auto-generation of CAP
        -  Support Iterable(type|MultiType), so that a type can be
          written as `list(str|int)` for a list of strs or ints.
            - This absolutely needs unit tested once implemented
        - Traverse and build CAPs for the configurable objects w/in MultiTypes.
        - Allow CAP to be generated and informed more by the config
          when a docstring specifies a parent class, and the config gives a
          child class that inherits from that parent and is still configurable.
          This is a common and important use case to support.
            - This absolutely needs unit tested once implemented
        -  !! Option to ignore the docs (especially when there are none in
          a 3rd party) and to instead be informed by the type hinting and
          defaults used in the python declaration of the function/method.
            - the point is to write once with docstrings, but if 3rd party's do
              not support complete docs because they rely on the python type
              hinting, then we should support it to for completion. All that
              really matters is it is written once somewhere, and when we don't
              have control over the code, we either support common trends in
              others or allow the user wrap such objects w/ their own written
              docstring, where the latter is a currently supported workaround
              at the expense of the user's time.
            - This absolutely needs unit tested once implemented
            - This feature is very important. Perhaps should separate from docstr and create a project that only traverses python objects with type hints and converts those type hinted functions, classes, methods, etc... into heirarchical ConfigArgParse objects.
                Check if such a project already exists!
                From there, docstr would depend on that underlying project to:
                - traverse the python specified (non-docstring) object graph
                - create a Nested/Hierarchical ConfigArgParse module from the type hints of an object
                - use the common place Python Type Hinting ([typing][https://docs.python.org/3/library/typing.html]) package as the standard of typing all objects and variables.
                    - thus all parsed docstring types would be converted into appropriate python typing objects.
                - support parsing of objects w/o doc-strings or prioritize type hinting over parsed types in the __doc__.
                - this would also provide a connection to any type checking packages that rely on type hinting.
        - doc linking, e.g., `see module.sub_module.class.method`
            - further doc linking support is necessary with more tests.
            - Perhaps the doc linking should be mimic that of importing modules.
                - `arg_name : see self` gets the docs for self.arg_name.
                    - Should be able to replace self with any import path to a class path.
                - `see self` : currently is `see all` adding everything from the linked object's docstring.
                - `see self.*` : This should be the new see all, or something similar.
                    This way it is purposeful to import everything and similar to `... import *`.
                    This avoids the issue when a class attributes has all init params and extra attributes that are not params, so if `see self` becomes "only include those that which are params in the input." then it does not include unwanted attributes as args.
                    However, if you use splat extention, this no longer works.
                    So perhaps also an easier way to grap a list of args from the linked object, rather than a chain of `args : see self`, which the prototype forces ppl to do now.
        - support of custom Sphinx napoleon
            - support of custom docstring parsers through Sphinx extentions.
        - Given an object whose doc string is fully parsed by docstr, output the template of the YAML config file to be editted.
        - The initialized program needs to have the option (possibly defaulting to) lazy initializing, such that  when the python interpretter gets to an object it then may be instantiated from the docstr CAP and values. Especially good for code that is massive in memory post init or takes a long time and you want to only execute it once necessary.
        - Properly handle sys.exit codes for docstr run programs! At the moment, if the main function/method returns something other than an exit code, it will end with a SystemExit error!
    - Code redundancy reduction using the docstrings:
        - Decorator for specifying the args and kwargs of a function with format as:
            `def func(*args, **kwargs):` to avoid redundant writing of args, defaults, etc.
        - Notably, "protected" attributes may be marked as such in the docs and so the user doesn't have to write @property variable name reutrn protected \_variable.
    - Type Checking based on Docstrings:
        - Decorator for optional runtime type-checking of variables values at runtime to the docstring's preset values.
    - [-TODO-] Extra features: features that are unnecessary, but beneficial
        - Parameter iteration and searching (possibly using `pyrameter` or `SHADHO`) to run multiple versions of the same pipeline using different parameters, either
            - This is specifically useful to Machine Learning (ML) researchers, but may be nice for those who either want to exhaustively run variations of their pipeline or have some objective function they want to optimize over different variations of their pipeline.
            - in ML, the pipeline and its parameter search would be entirely contained all in one yaml file, or multiple through optoinal config linking.
                This would result in a straightforward overview of the ML experiment pipeline, easily swapped with existing modules written in code as classes.
        - Possibly rely upon Apache AirFlow DAG for the pipelining.
            - `dag-factory` : AirFlow extension to make dynamic
            - alternative to AirFlow is `dagster`

### Verisoning

Docstr uses [Semantic Versioning 2.0.0](https://semver.org/spec/v2.0.0.html).
Docstr's version will remain < 1.0.0 until adequate unit test coverage exists.

### License

The docstr project is licensed under the MIT license, which is provided in LICENSE.txt
