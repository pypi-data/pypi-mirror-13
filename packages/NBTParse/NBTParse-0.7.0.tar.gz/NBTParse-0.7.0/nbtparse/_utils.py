"""Assorted utilities.

This module and all of its contents are implementation details.  Their
interfaces are subject to change at any time and should not be relied upon
outside of NBTParse implementation code.  The entire module may cease to exist
in future versions of NBTParse.

Nevertheless, some of the materials in this module might prove useful to
non-implementation code.  Reusers are encouraged to copy (with attribution as
per the copyright license) portions of this file piecemeal into other
projects.

"""

import importlib

def Sentinel(module_name, object_name, docstring):
    """Factory function for creating sentinel values."""
    repr_result = '{}.{}'.format(module_name, object_name)
    def __reduce__(self):
        return (_find_sentinel, (module_name, object_name))
    cls = type('_Sentinel', (), {
                                '__doc__': docstring,
                                '__reduce__': __reduce__,
                                '__repr__': (lambda _: repr_result),
                                '__slots__': (),
                               })
    result = cls()
    return result


def _find_sentinel(module_name, object_name):
    """Helper function for unpickling.

    Don't use.

    """
    module = importlib.import_module(module_name)
    return getattr(module, object_name)
