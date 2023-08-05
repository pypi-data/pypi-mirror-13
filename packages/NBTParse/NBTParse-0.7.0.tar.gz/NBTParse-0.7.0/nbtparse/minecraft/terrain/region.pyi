import typing as ty

from .. import entity_ids
from . import chunk


AnyNamespace = ty.Union[entity_ids.Namespace, entity_ids.FrozenNamespace]


class Region(ty.MutableMapping[ty.Tuple[int, int], chunk.Chunk]):
    def __init__(self, region_x: int, region_z: int,
                 namespace: AnyNamespace=entity_ids.VANILLA) -> None:
        ...

    @classmethod
    def load(cls, region_x: int, region_z: int, src: ty.io.BinaryIO,
             namespace: AnyNamespace=entity_ids.VANILLA) -> 'Region':
        ...

    def save(self, dest: ty.io.BinaryIO) -> None:
        ...
