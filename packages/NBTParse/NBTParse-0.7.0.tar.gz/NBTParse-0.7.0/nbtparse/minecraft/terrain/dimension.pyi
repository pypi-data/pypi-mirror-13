import abc
import pathlib
import typing as ty

from . import chunk
from . import voxel
from .. import entity_ids


XYCoords = ty.Tuple[int, int]
XYZCoords = ty.Tuple[int, int, int]
XYZSlice = ty.Tuple[slice, slice, slice]
RegionLike = ty.MutableMapping[XYCoords, chunk.Chunk]
AnyNamespace = ty.Union[entity_ids.Namespace, entity_ids.FrozenNamespace]
AnyPath = ty.Union[pathlib.Path, str]


class RegionManager(metaclass=abc.ABCMeta):
    @abc.abstractmethod
    def get_region(self, r_x: int, r_z: int,
                   require_exist: bool=True) -> RegionLike:
        ...

    def release(self) -> None:
        ...

    def close(self) -> None:
        ...


R = TypeVar('R', bound=RegionManager)

class Dimension(Generic[R]):
    def __init__(self, regions: R, *, fill_value: voxel.Block=None,
                 namespace: AnyNamespace=entity_ids.VANILLA) -> None:
        ...

    def close(self) -> None:
        ...

    def __enter__(self) -> 'Dimension':
        ...

    def __exit__(self, exc1, exc2, exc3) -> bool:
        ...

    def __getitem__(self, index: XYZSlice) -> voxel.VoxelBuffer:
        ...

    @ty.overload
    def __getitem__(self, index: XYZCoords) -> voxel.Block:
        ...

    def __setitem__(self, index: XYZSlice, value: voxel.VoxelBuffer) -> None:
        ...

    @ty.overload
    def __setitem__(self, index: XYZCoords, value: voxel.Block) -> None:
        ...

    @property
    def entities(self) -> '_EntitySliceable':
        ...

    @property
    def regions(self) -> R:
        ...


class FileRegionManager(RegionManager):
    def __init__(self, path: AnyPath, max_cache: int,
                 namespace: AnyNamespace=entity_ids.VANILLA) -> None:
        ...

    def save_all(self) -> None:
        ...

    def save_fast(self) -> None:
        ...

    @property
    def atomic(self) -> '_AtomicContext':
        ...

    def recover_atomic(self) -> bool:
        ...

    @property
    def max_cache(self) -> ty.Optional[int]:
        ...
    @max_cache.setter
    def max_cache(self, new_max_cache: ty.Optional[int]) -> None:
        ...

    @property
    def cache_size(self) -> int:
        ...

    def get_region(self, r_x: int, r_z: int,
                   require_exist: bool=True) -> region.Region:
        ...

    def flush_cache(self, *, save=True) -> None:
        ...


FSDimension = Dimension[FileRegionManager]
# A dimension backed by the filesystem


def open(path: AnyPath, *, max_cache: int=5, fill_value: voxel.Block=None,
         namespace: AnyNamespace=entity_ids.VANILLA) -> FSDimension:
    ...


# NB: Classes beyond this point are not part of the public API, except
# to the extent that the public API returns instances of them.
# Don't assume these classes will always have these names or that you can
# instantiate them directly.


class _EntitySliceable:
    def __getitem__(self, idx: XYZSlice) -> ty.Set[entity.Entity]:
        ...

    def __setitem__(self, idx: XYZSlice,
                    value: ty.Iterable[entity.Entity]) -> None:
        ...

    def __delitem__(self, idx: XYZSlice) -> None:
        ...

class _AtomicContext(contextlib.ContextDecorator):
    def __enter__(self) -> None:
        ...

    def __exit__(self, exc_type, exc_value, traceback) -> bool:
        ...
