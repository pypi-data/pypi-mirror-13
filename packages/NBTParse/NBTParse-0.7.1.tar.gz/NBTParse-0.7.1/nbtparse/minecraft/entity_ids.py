import collections
import collections.abc as cabc
import logging
import types
import weakref

from .. import exceptions


logger = logging.getLogger(__name__)


_REGISTERED_CLASSES = collections.defaultdict(weakref.WeakValueDictionary)
# Keys: module name (string)
# Values: dictionaries mapping identifier strings to classes


class Namespace(cabc.MutableMapping):
    """Namespace of entities.

    Maps identifier strings to classes.  Temporary classes are automatically
    removed from the namespace when they die.

    .. warning::

        If a class is automatically removed from the namespace while iterating
        over the namespace, undefined behavior occurs.  See :mod:`weakref` for
        more information.

    """
    def __init__(self, *args, **kwargs):
        self._mapping = weakref.WeakValueDictionary()
        super().__init__(*args, **kwargs)

    def __repr__(self):
        return '<Namespace (entity_ids): {!r} entries>'.format(len(self))

    def __getitem__(self, key):
        return self._mapping[key]

    def __setitem__(self, key, value):
        self._mapping[key] = value

    def __delitem__(self, key, value):
        del self._mapping[key]

    def __iter__(self):
        return iter(self._mapping)

    def __len__(self):
        return len(self._mapping)

    def freeze(self) -> 'FrozenNamespace':
        """Return a :class:`FrozenNamespace` equivalent to this one."""
        return FrozenNamespace(self)

    def register_all(self, module: types.ModuleType):
        """Register a whole module.

        Registers every Entity subclass declared at the top level of the
        provided module with the identifier used in its class declaration.
        Identifiers already in the namespace are overwritten.  Classes without
        identifiers are skipped.
        
        Also registers any classes explicitly decorated with
        :func:`register_class`, regardless of where they are declared,
        provided they have not been garbage collected.

        """
        self.update(_REGISTERED_CLASSES[module.__name__])


class FrozenNamespace(cabc.Mapping):
    """Immutable namespace of entities.

    Maps identifier strings to classes.  Temporary classes are kept alive by
    being in the mapping.

    """
    def __init__(self, *args, **kwargs):
        self._mapping = dict(*args, **kwargs)

    def __repr__(self):
        return ('<FrozenNamespace (entity_ids): {!r} entries>'
                .format(len(self)))

    def __getitem__(self, key):
        return self._mapping[key]

    def __iter__(self):
        return iter(self._mapping)

    def __len__(self):
        return len(self._mapping)

    def thaw(self) -> Namespace:
        """Return a :class:`Namespace` equivalent to this one."""
        return Namespace(self)


def register_class(ident: str) -> callable:
    """Decorator to register a class with the entity IDs system.

    Usually called automatically from :class:`entity.EntityMeta`; you should
    not need to call this yourself.

    """
    def decorator(class_: 'entity.EntityMeta') -> 'entity.EntityMeta':
        module_name = class_.__module__
        _REGISTERED_CLASSES[module_name][ident] = class_
        return class_
    return decorator


_VANILLA = Namespace()

VANILLA = None
"""The :class:`FrozenNamespace` containing all vanilla entities."""

def _extend_vanilla(module: types.ModuleType):
    _VANILLA.register_all(module)


def _finish_vanilla():
    global VANILLA
    global _VANILLA
    VANILLA = _VANILLA.freeze()
    del _VANILLA
