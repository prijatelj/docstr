from importlib import import_module
__version__='0.0.1'

__all__ = [
    'cli',
    'configargparse',
    'docstring',
    'parsing',
]

for module in __all__:
    globals()[module] = import_module(f'.{module}', __name__)
del import_module, module

__all__ += ['parse', 'parse_config']
from .parsing import parse, parse_config
