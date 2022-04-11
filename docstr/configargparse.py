"""ConfigArgParse specific extentions or utils for docstr."""
import configargparse as cap


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


# TODO str conversion into objects of expected types
#   This is already supported for "common built-in types and functions".
#   TODO get object from a string of the fully qualified name in python.
#   TODO get the object from the string of relative to the docstr cli's object's module.


# TODO Argument multiple accepted types matching docstr.docstrings.MultiType


# TODO Argument requirement dependency on values of other args.


# TODO Perhaps, find/make a nice formatter_class for customized help output?

def get_configargparser(
    docstring,
    parser=None,
    nested_positionals=False,
    config_file_parser='yaml',
):
    """Creates the ConfigArgParser from contents in the given docstr.Docstring.

    Args
    ----
    docstring : ClassDocstring | FuncDocstring
    parser : ArgParser | argparse._ArgumentGroup = None
        A pre-existing parser object to be extended with a parser for this
        ClassDocstring's configurable initialization arguments.
    neted_positionals : bool = False
        If True, then the nested parser created here and below through
        recursive calling will allow positional arguments for required
        arguments instead of keyword required arguments. The default is
        False, meaning any required argument is made as a required keyword
        argument, non-positional.
    """
    if isinstance(docstring, ClassDocstring):
        description = \
            f'{docstring.description}\n \n'{docsring.init.description}'
        # TODO store the object in type to recreate the object post CAP parse
        args = docstring.init.args
    elif isinstance(docstring, FuncDocstring):
        description = docstring.description
        # TODO store the object in type to recreate the object post CAP parse
        args = docstring.args
    elif isinstance(docstring, Docstring):
        raise TypeError(' '.join([
            '`docstring` is an unsupported subclass of `docstr.Docstring`.',
            f'Expected ClassDocstring or FuncDocstring, not: {type(docstring}'
        ]))
    else:
        raise TypeError(f'Unexpected `docstring` type: {type(docstring)}')

    # Setup the nested parser / argument_group
    if parser is None:
        if config_file == 'yaml':
            config_file_parser = cap.YAMLConfigFileParser
        elif config_file == 'ini':
            config_file_parser = cap.ConfigparserConfigFileParser
        else:
            raise ValueError(f'Unexpected `config_file` value: {config_file}')
        parser = cap.ArgParser(
            prog=docstring.name,
            description=description,
            config_file_parser_class=config_file_parser,
        )
    elif isinstance(parser, {ArgParser, argparse._ArgumentGroup}):
        # Create the subparsers and pass that down any recursive get_cap()
        # TODO Once a Nested Parser is supported, replace this w/ that
        # This should never occur if docstr cli is used, as that makes
        # the base parser, which already added subparsers

        # TODO handle name prefix for nesting!
        nested_parser = parser.add_argument_group(
            f'{self.name}',
            description,
        )
    else:
        raise TypeError(f'Unexpected `parser` type: {type(parser)}')

    # TODO set args from __init__ for ClassDocstrings
    #init_parser = self.init_docstring.get_cap(parser)

    # TODO set args from __init__ for ClassDocstrings

    # TODO For any subclasses of Docstring, recursive call get_cap()

    return parser
