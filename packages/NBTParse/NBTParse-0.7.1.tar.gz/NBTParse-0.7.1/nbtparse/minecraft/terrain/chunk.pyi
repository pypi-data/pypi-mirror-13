import typing as ty

from ...syntax import ids
from .. import entity_ids
from .. import nbtobject
from . import voxel


AnyNamespace = ty.Union[entity_ids.Namespace, entity_ids.FrozenNamespace]
HeightMap = ty.MutableMapping[ty.Tuple[int, int], int]


class Section(nbtobject.NBTObject):
    @property
    def y_index(self) -> int:
        ...

    @y_index.setter
    def y_index(self, value: int) -> None:
        ...

    @property
    def blocks(self) -> voxel.VoxelBuffer:
        ...

    @blocks.setter
    def blocks(self, value: voxel.VoxelBuffer) -> None:
        ...


class Chunk(nbtobject.NBTObject):
    @property
    def sections(self) -> ty.MutableMapping[int, Section]:
        ...

    @sections.setter
    def sections(self, value: ty.MutableMapping[int, Section]) -> None:
        ...

    @property
    def entities(self) -> ty.List[entity.Entity]:
        ...

    @entities.setter
    def entities(self, value: ty.List[entity.Entity]) -> None:
        ...

    @property
    def height_map(self) -> HeightMap:
        ...

    @height_map.setter
    def height_map(self, value: HeightMap) -> None:
        ...

    @staticmethod
    def prepare_save(nbt: tags.CompoundTag) -> tags.CompoundTag:
        ...

    @staticmethod
    def prepare_load(nbt: tags.CompoundTag) -> tags.CompoundTag:
        ...
