import typing as ty

import numpy as np

from . import tile

class Block:
    def __init__(self, id: int, data: int=0) -> None:
        ...

    @property
    def id(self) -> int:
        ...

    @property
    def data(self) -> int:
        ...


Coords = ty.Tuple[int, int, int]
TileMap = ty.MutableMapping[Coords, tile.TileEntity]
WatchCallback = ty.Callable[[ty.Union[Coords, ty.Tuple[range, range, range]]],
                            object]


class VoxelBuffer:
    def __init__(self, length: int, height: int, width: int) -> None:
        ...

    @property
    def length(self) -> int:
        ...

    @property
    def width(self) -> int:
        ...

    @property
    def height(self) -> int:
        ...

    @property
    def tilemap(self) -> TileMap:
        ...

    def __len__(self) -> int:
        ...

    def __array__(self) -> np.ndarray:
        ...

    def watch(self, observer: WatchCallback) -> None:
        ...

    def unwatch(self, observer: WatchCallback) -> None:
        ...

    def __getitem__(self, index: Coords) -> Block:
        ...

    def __setitem__(self, index: Coords, value: Block) -> None:
        ...

    @classmethod
    def from_raw(cls, ids: bytes, addids: bytes, damages: bytes, length: int,
                 height: int, width: int) -> 'VoxelBuffer':
        ...

    def to_raw(self) -> ty.Tuple[bytes, bytes, bytes]:
        ...

    def enumerate(self) -> ty.Iterator[ty.Tuple[Coords, Block]]:
        ...

    def xyz(self) -> ty.Iterator[ty.Tuple[Coords, Block]]:
        ...

    def __iter__(self) -> ty.Iterator[Block]:
        ...

    def __reversed__(self) -> ty.Iterator[Block]:
        ...
