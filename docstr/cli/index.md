## Docstr CLI

This is the code that specifies the docstr command line interface that is installed alongside the docstr package.

### CLI Funcitonality

The following are subparsers of docstr that support different functionality.
- parse: `docstr parse ...`
    - Call docstr.parse() on the given object(s) with the specified parser arguments.
- compile: `docstr compile ...`
- run: `docstr run ...`

#### Optional Functionality Under Consideration

- man: `docstr man ...`
    - generate man pages to save/read from the docs of the docstr parsed objects
