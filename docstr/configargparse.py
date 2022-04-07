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
