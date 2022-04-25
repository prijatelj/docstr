from importlib import import_module

__all__ = [
    'cli',
]

for module in __all__:
    globals()[module] = import_module(f'.{module}', __name__)
del import_module, module
