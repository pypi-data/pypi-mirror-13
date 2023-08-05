"""
overload.py

A simple function overload decorator that mostly works.
It makes an heavy use of annotation and thus may not be as pythonic as it
should.

"""

import inspect

class overload:
    functions = dict()
    def __init__(self, f):
        self.f = f
        funsig = inspect.signature(f)
        key = '{}_{}'.format(f.__name__, '_'.join([str(a.annotation) for a in
            funsig.parameters.values()]))
        overload.functions[key] = f
    
    def __call__(self, *args):
        funsig = inspect.signature(self.f)
        key = '{}_{}'.format(self.f.__name__, '_'.join([str(type(a)) for a in
            args]))
        overload.functions[key](*args)
