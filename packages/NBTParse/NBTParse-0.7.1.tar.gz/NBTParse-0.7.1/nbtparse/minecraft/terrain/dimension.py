import abc
import collections
import collections.abc as cabc
import contextlib
import errno
import functools
import itertools
import logging
import os
import pathlib

from ...exceptions import ConcurrentError
from .. import entity
from .. import entity_ids
from .. import entityfactory
from . import voxel
from . import region
from . import chunk


logger = logging.getLogger(__name__)


CHUNK_BLOCKS = 16  # to a side
REGION_CHUNKS = 32  # to a side
REGION_BLOCKS = CHUNK_BLOCKS * REGION_CHUNKS

SECTIONS_PER_CHUNK = 16

HEIGHT_LIMIT = SECTIONS_PER_CHUNK * CHUNK_BLOCKS

FIRST_DOTFILE = '.phase1-inprogress'
SECOND_DOTFILE = '.phase2-inprogress'

TMP_FORMAT = 'r.{}.{}.mca.tmp'

TMP_GLOB = '*.mca.tmp'

REGION_FORMAT = 'r.{}.{}.mca'


try:
    fsync = os.fdatasync
except AttributeError:
    fsync = os.fsync


def _cache_correct(meth):
    """Decorator for public-facing methods which may enlarge the cache.

    Automatically flush the cache when the method returns.

    """
    @functools.wraps(meth)
    def wrapper(self, *args, **kwargs):
        try:
            return meth(self, *args, **kwargs)
        finally:
            self._flush_cache()
    return wrapper


class RegionManager(metaclass=abc.ABCMeta):
    """Abstract class for managing region objects.

    Implementations are responsible for creating and caching region objects,
    or objects which are duck-type compatible with regions.  In `PEP 484`_
    notation, the required duck type is as follows::

        typing.MutableMapping[typing.Tuple[int, int], chunk.Chunk]

    .. _PEP 484: https://www.python.org/dev/peps/pep-0484/

    The primary consumer of this interface is :class:`Dimension`.  Other
    classes may use it, but for simplicity, this documentation refers to the
    API consumer as a "dimension."

    .. note::

        The key words "MUST", "MUST NOT", "REQUIRED", "SHALL", "SHALL NOT",
        "SHOULD", "SHOULD NOT" "RECOMMENDED", "MAY", and "OPTIONAL" in this
        document are to be interpreted as described in `RFC 2119`_\ .

        .. _RFC 2119: https://www.ietf.org/rfc/rfc2119.txt

    """
    @abc.abstractmethod
    def get_region(self, r_x: int, r_z: int,
                   require_exist: bool=True):
        """Return the region at the given coordinates.

        An implementation MUST satisfy these invariants:

        * The dimension MAY mutate the return value of this method in-place.
          Any changes made SHALL be preserved in future calls to this method.

        * The dimension SHOULD periodically call :meth:`release`.  After it
          does so, the dimension SHALL NOT modify any regions without first
          reacquiring them from this method.

        * If require_exist is True and a region does not exist, an
          :exc:`IndexError` SHALL be raised.  Existence is
          implementation-defined, but SHALL be internally consistent.

        * If require_exist is False, an :exc:`IndexError` SHALL NOT be raised;
          if the region does not exist, an empty region SHALL be returned.

        * Regions SHALL NOT be created except at the request of the dimension,
          but implementations MAY prune empty regions (regions which contain
          no chunks).  Said pruning SHALL only take place when :meth:`release`
          is called.

        .. note::

            Coordinates are region coordinates, not block or chunk
            coordinates.  Floor-divide chunk coordinates by 32 to get region
            coordinates.

        """
        raise NotImplementedError()

    def release(self):
        """Hook method called when regions are no longer needed.

        Affects the semantics of :meth:`get_region`.  Briefly, once this is
        called, the implementation is no longer required to persist changes
        made to regions in-place.  Implementations which engage in caching of
        region objects MAY flush or evict them here.  Other implementations
        MAY take housekeeping actions appropriate to their specific needs.

        The default implementation does nothing, since some implementations
        might not need to take any action in this case.

        """
        pass

    def close(self):
        """Hook method called when the Dimension is closed.

        Implementations MAY save regions to disk or other persistence
        mechanisms at this time.  Implementations which consume a lot of
        memory or other resources SHOULD make reasonable efforts to minimize
        their resource consumption after this method returns.

        The default implementation does nothing, since some implementations
        might not need to take any action in this case.

        The dimension SHALL NOT call any method other than :meth:`close` after
        the first call to :meth:`close`.  Subsequent calls SHALL succeed and
        do nothing.  Implementations MAY fail fast if the dimension
        violates this contract.

        """
        pass


class Dimension:
    """A dimension, in Minecraft terms.

    A collection of (usually) contiguous regions.

    May be indexed and sliced using block coordinates.  Indexing is similar to
    that of :class:`.voxel.VoxelBuffer`, except that X and Z coordinates are
    absolute, and X and Z slices must have both a start and an end.

    Dimensions may also be used as a context manager, to automatically call
    :meth:`close`::

        with dimension.open('foo/bar') as baz:
            # Do things

    Dimensions are not thread-safe.

    """
    def __init__(self, regions: RegionManager, *,
                 fill_value: voxel.Block=None,
                 namespace=entity_ids.VANILLA):
        #: Namespace to use for entities.
        self.namespace = namespace
        #: Value to fill in when slicing into missing regions or chunks
        self.fill_value = fill_value
        #: :class:`RegionManager` to use when retrieving regions.
        self.regions = regions
        self._closed = False

    def __repr__(self):
        return '<Dimension: regions={!r}>'.format(self.regions)

    def close(self):
        """Close this dimension.

        Once closed, a dimension is no longer usable.  Closing multiple times
        is legal and has no effect.

        Some region managers, such as :class:`FileRegionManager`, require
        closing the dimension to ensure all data is saved properly.

        .. warning::

            Dimensions do not automatically close themselves when garbage
            collected.  You must close them explicitly.

        """
        if self._closed:
            return
        self.regions.close()
        self._closed = True

    def __enter__(self):
        return self

    def __exit__(self, exc1, exc2, exc3):
        self.close()
        return False  # do not suppress exceptions

    def _flush_cache(self, save=True):
        """Remove extraneous items from the cache.

        Bring the cache size down to :obj:`max_cache`.  Also invalidates any
        regions discarded from the cache, so use with care.  If save is False,
        regions are not saved; this should only be used if you have saved them
        by hand somewhere else.

        """
        self.regions.release()

    def _getregion(self, r_x: int, r_z: int) -> region.Region:
        """Retrieve and return the region r_x, r_z.

        Region will be cached; you are responsible for flushing the cache when
        it is no longer needed.

        """
        require_exist = self.fill_value is None
        return self.regions.get_region(r_x, r_z, require_exist)

    def _getchunk(self, c_x: int, c_z: int) -> chunk.Chunk:
        """Retrieve and return the chunk c_x, c_z.

        You must flush the cache after.

        """
        r_x = c_x // REGION_CHUNKS
        r_z = c_z // REGION_CHUNKS
        r = self._getregion(r_x, r_z)
        try:
            return r[c_x, c_z]
        except KeyError as exc:
            if self.fill_value is None:
                raise IndexError('Chunk {}, {} does not exist'
                                 .format(c_x, c_z)) from exc
            logger.info('Chunk %d, %d does not exist, filling in %r', c_x,
                        c_z, self.fill_value)
            cnk = chunk.Chunk()
            for y in range(SECTIONS_PER_CHUNK):
                sec = chunk.Section()
                sec.blocks[...] = self.fill_value
                cnk.sections[y] = sec
            r[c_x, c_z] = cnk
            return cnk

    def _getsection(self, s_x: int, s_y: int, s_z: int) -> chunk.Section:
        """Retrieve and return the section s_y in chunk s_x, s_z.

        You must flush the cache after.

        """
        c = self._getchunk(s_x, s_z)
        return c.sections[s_y]

    def _getsection_byblock(self, b_x: int, b_y: int,
                            b_z: int) -> chunk.Section:
        """Same as _getsection, but use block coordinates."""
        c_x = b_x // CHUNK_BLOCKS
        c_y = b_y // CHUNK_BLOCKS
        c_z = b_z // CHUNK_BLOCKS
        s = self._getsection(c_x, c_y, c_z)
        return s

    def _getblock(self, b_x: int, b_y: int, b_z: int) -> voxel.Block:
        """Retrieve and return a single block.

        You must flush the cache.

        """
        s = self._getsection_byblock(b_x, b_y, b_z)
        x = b_x % CHUNK_BLOCKS
        y = b_y % CHUNK_BLOCKS
        z = b_z % CHUNK_BLOCKS
        return s.blocks[x, y, z]

    def _setblock(self, b_x: int, b_y: int, b_z: int, value: voxel.Block):
        """Replace a single block.

        You must flush the cache.

        """
        s = self._getsection_byblock(b_x, b_y, b_z)
        x = b_x % CHUNK_BLOCKS
        y = b_y % CHUNK_BLOCKS
        z = b_z % CHUNK_BLOCKS
        s.blocks[x, y, z] = value

    def _make_chunk_range(self, x_slice: slice, y_slice: slice,
                          z_slice: slice) -> (range, range, range):
        # Simplify the slice into one with a step of +1
        # Caller can compute the real slice later
        x_start = min(x_slice.start, x_slice.stop)
        y_start = min(y_slice.start, y_slice.stop)
        z_start = min(z_slice.start, z_slice.stop)
        x_stop = max(x_slice.start, x_slice.stop)
        y_stop = max(y_slice.start, y_slice.stop)
        z_stop = max(z_slice.start, z_slice.stop)

        # Make ranges for the affected chunks
        x_chunk_range = range(x_start // CHUNK_BLOCKS,
                              x_stop // CHUNK_BLOCKS +
                              # Round up if there's a remainder:
                              (1 if x_stop % CHUNK_BLOCKS else 0))
        y_chunk_range = range(y_start // CHUNK_BLOCKS,
                              y_stop // CHUNK_BLOCKS +
                              (1 if y_stop % CHUNK_BLOCKS else 0))
        z_chunk_range = range(z_start // CHUNK_BLOCKS,
                              z_stop // CHUNK_BLOCKS +
                              (1 if z_stop % CHUNK_BLOCKS else 0))
        return (x_chunk_range, y_chunk_range, z_chunk_range)

    def _get_chunk_slice(self, x_chunk_range: range, y_chunk_range: range,
                         z_chunk_range: range) -> voxel.VoxelBuffer:
        """Obtain a VoxelBuffer of the chunks around the given slices."""
        # Prepare a temporary buffer to hold all the chunks we need
        x_size = len(x_chunk_range) * CHUNK_BLOCKS
        y_size = len(y_chunk_range) * CHUNK_BLOCKS
        z_size = len(z_chunk_range) * CHUNK_BLOCKS
        vb = voxel.VoxelBuffer(x_size, y_size, z_size)

        # Figure out the origin of the buffer
        x_base_chunk = x_chunk_range.start
        y_base_chunk = y_chunk_range.start
        z_base_chunk = z_chunk_range.start

        # Grab all the required sections into vb
        product = itertools.product(x_chunk_range, y_chunk_range,
                                    z_chunk_range)
        for x_chunk, y_chunk, z_chunk in product:
            sec = self._getsection(x_chunk, y_chunk, z_chunk)
            x_start = (x_chunk - x_base_chunk)*CHUNK_BLOCKS
            y_start = (y_chunk - y_base_chunk)*CHUNK_BLOCKS
            z_start = (z_chunk - z_base_chunk)*CHUNK_BLOCKS
            x_stop = x_start + CHUNK_BLOCKS
            y_stop = y_start + CHUNK_BLOCKS
            z_stop = z_start + CHUNK_BLOCKS
            vb[x_start:x_stop,
               y_start:y_stop,
               z_start:z_stop] = sec.blocks

        return vb

    def _set_chunk_slice(self, x_chunk_range: range, y_chunk_range: range,
                         z_chunk_range: range, vb: voxel.VoxelBuffer):
        # Figure out the origin of the buffer
        x_base_chunk = x_chunk_range.start
        y_base_chunk = y_chunk_range.start
        z_base_chunk = z_chunk_range.start

        # For every section:
        product = itertools.product(x_chunk_range, y_chunk_range,
                                    z_chunk_range)
        for x_chunk, y_chunk, z_chunk in product:
            sec = self._getsection(x_chunk, y_chunk, z_chunk)
            x_start = (x_chunk - x_base_chunk)*CHUNK_BLOCKS
            y_start = (y_chunk - y_base_chunk)*CHUNK_BLOCKS
            z_start = (z_chunk - z_base_chunk)*CHUNK_BLOCKS
            x_stop = x_start + CHUNK_BLOCKS
            y_stop = y_start + CHUNK_BLOCKS
            z_stop = z_start + CHUNK_BLOCKS
            sec.blocks[...] = vb[x_start:x_stop, y_start:y_stop,
                                 z_start:z_stop]

    def _slice_cleanup(self, x_slice: slice, y_slice: slice,
                       z_slice: slice) -> (slice, slice, slice):
        # Y is special because of the height limit
        # Allow negatives and wraparound
        y_slice = slice(*y_slice.indices(HEIGHT_LIMIT))

        # Fill in missing steps
        if x_slice.step is None:
            x_slice = slice(x_slice.start, x_slice.stop, 1)
        if z_slice.step is None:
            z_slice = slice(z_slice.start, z_slice.stop, 1)
        index = (x_slice, y_slice, z_slice)
        if any(x.step == 0 for x in index):
            raise ValueError('Step cannot be zero')
        if any(x.start is None or x.stop is None for x in index):
            raise ValueError('Indefinite slices not allowed')
        return x_slice, y_slice, z_slice

    @_cache_correct
    def __getitem__(self, index):
        if type(index) is not tuple or len(index) != 3:
            raise TypeError('Indexing is three-dimensional')
        if all(type(x) is int for x in index):
            x, y, z = index
            logger.info('Retrieving single block %r, %r, %r', x, y, z)
            return self._getblock(x, y, z)
        elif all(type(x) is slice for x in index):
            x_slice, y_slice, z_slice = self._slice_cleanup(*index)
            logger.info('Slicing dimension to %r, %r, %r',
                        x_slice, y_slice, z_slice)

            x_range, y_range, z_range = self._make_chunk_range(x_slice,
                                                               y_slice,
                                                               z_slice)

            # Obtain the chunk slice:
            vb = self._get_chunk_slice(x_range, y_range, z_range)

            x_base_chunk = x_range.start
            y_base_chunk = y_range.start
            z_base_chunk = z_range.start

            # Finally, take a slice out of vb
            # Transform the given absolute coordinates into relative
            # coordinates:
            x_start = x_slice.start - x_base_chunk*CHUNK_BLOCKS
            x_stop = x_slice.stop - x_base_chunk*CHUNK_BLOCKS
            x_step = x_slice.step
            y_start = y_slice.start - y_base_chunk*CHUNK_BLOCKS
            y_stop = y_slice.stop - y_base_chunk*CHUNK_BLOCKS
            y_step = y_slice.step
            z_start = z_slice.start - z_base_chunk*CHUNK_BLOCKS
            z_stop = z_slice.stop - z_base_chunk*CHUNK_BLOCKS
            z_step = z_slice.step

            return vb[x_start:x_stop:x_step, y_start:y_stop:y_step,
                      z_start:z_stop:z_step]

        else:
            raise TypeError('Must use slices or indices and not a '
                            'combination of both')

    @_cache_correct
    def __setitem__(self, index, value):
        if type(index) is not tuple or len(index) != 3:
            raise TypeError('Indexing is three-dimensional')
        if all(type(x) is int for x in index):
            if type(value) is not voxel.Block:
                raise TypeError('Individual elements must be Block, not '
                                '{}'.format(type(value).__name__))
            x, y, z = index
            self._setblock(x, y, z, value)
        elif all(type(x) is slice for x in index):
            if type(value) is not voxel.VoxelBuffer:
                raise TypeError('Slice assignment must be VoxelBuffer, not '
                                '{}'.format(type(value).__name__))
            x_slice, y_slice, z_slice = self._slice_cleanup(*index)

            x_range, y_range, z_range = self._make_chunk_range(x_slice,
                                                               y_slice,
                                                               z_slice)

            # Obtain the chunk slice:
            vb = self._get_chunk_slice(x_range, y_range, z_range)

            x_base_chunk = x_range.start
            y_base_chunk = y_range.start
            z_base_chunk = z_range.start

            # Finally, put a slice into vb
            # Transform the given absolute coordinates into relative
            # coordinates:
            x_start = x_slice.start - x_base_chunk*CHUNK_BLOCKS
            x_stop = x_slice.stop - x_base_chunk*CHUNK_BLOCKS
            x_step = x_slice.step
            y_start = y_slice.start - y_base_chunk*CHUNK_BLOCKS
            y_stop = y_slice.stop - y_base_chunk*CHUNK_BLOCKS
            y_step = y_slice.step
            z_start = z_slice.start - z_base_chunk*CHUNK_BLOCKS
            z_stop = z_slice.stop - z_base_chunk*CHUNK_BLOCKS
            z_step = z_slice.step

            vb[x_start:x_stop:x_step, y_start:y_stop:y_step,
               z_start:z_stop:z_step] = value
            self._set_chunk_slice(x_range, y_range, z_range, vb)
        else:
            raise TypeError('Must use slices or indices and not a '
                            'combination of both')

    @property
    def entities(self):
        """Sliceable collection of entities.

        Provides a similar slicing API to the dimension itself, except that
        extended slicing and ordinary indexing are unsupported.  Slicing the
        object returns a set of entities.  Slices may also be assigned to and
        deleted.  As with dimensions, all slices must be fully-qualified,
        except for Y-dimension slices.  Unlike with dimensions, slice indices
        may be fractional.

        Other collection-related operations are not currently supported.

        .. note::

            The slices are sets, not lists.  Duplicate entities with the same
            UUID and type are not supported and will be silently coalesced.

        """
        return _EntitySliceable(self)


def open(path: str, *, max_cache: int=5, fill_value: voxel.Block=None,
         namespace=entity_ids.VANILLA) -> Dimension:
    """Create a new :class:`Dimension` object.

    Return value is backed by a :class:`FileRegionManager`.  All arguments
    passed to this function are forwarded to the appropriate constructors.

    """
    regions = FileRegionManager(path, max_cache, namespace)
    return Dimension(regions, fill_value=fill_value, namespace=namespace)


class FileRegionManager(RegionManager):
    """:class:`RegionManager` backed by the filesystem.

    Regions are stored and retrieved from disk in the specified path.  A cache
    of regions is also maintained, and can be manipulated with these methods.

    The files get names like those in a typical Minecraft world.

    """
    def __init__(self, path: str, max_cache: int,
                 namespace=entity_ids.VANILLA):
        self.path = pathlib.Path(path)
        """Path to the dimension directory."""
        self.cache = collections.OrderedDict()
        self._max_cache = max_cache
        self._atomic = False
        self._namespace = namespace

    def __repr__(self):
        return '<FileRegionManager: path={!r}>'.format(self.path)

    def _sync_directory(self):
        if os.name == 'nt':
            # This does not work on NT
            logger.debug('Skip fsync() of directory %s (because Windows)',
                         self.path)
            return
        path = str(self.path)
        fd = os.open(path, os.O_RDONLY)
        try:
            logger.debug('fsync() directory %s', self.path)
            fsync(fd)
        finally:
            os.close(fd)

    def save_all(self):
        """Save every region currently cached.

        Regions which are no longer cached have already been saved.

        Prefer correctness over speed; provide the same guarantees as
        :obj:`FileRegionManager.atomic`.

        A :exc:`~.exceptions.ConcurrentError` is raised if another save
        appears to have been in progress when this method was called.  Under
        no circumstances are two or more :meth:`save_all` calls allowed to run
        concurrently on the same directory; all but one will always fail with
        an exception.

        If an exception is raised under other circumstances, it is recommended
        to call :meth:`recover_atomic`.

        """
        # Do a two-phase commit
        # Touch dotfiles to mark which phase of commit we're in.
        phase_1_path = self.path / FIRST_DOTFILE
        phase_2_path = self.path / SECOND_DOTFILE

        try:
            phase_1_path.touch(exist_ok=False)
        except FileExistsError as exc:
            raise ConcurrentError('Dimension directory is dirty') from exc
        self._sync_directory()

        # Phase 1: save all regions to temporary files.
        # If this fails, we can just remove them
        for region in self.cache.values():
            tmp_path = (self.path /
                        TMP_FORMAT.format(*region.coords))
            with tmp_path.open(mode='wb') as tmp_file:
                region.save(tmp_file)
                tmp_file.flush()
                fsync(tmp_file.fileno())

        # Don't need exist_ok since we created the phase 1 file
        # If someone else left the phase 2 file behind, they were done anyway
        phase_2_path.touch()
        # The phase 1 dotfile is left in place so other processes attempting
        # to interact with the dimension using this code will fail to create
        # the file
        self._sync_directory()

        # Phase 2: Move the temporary files over the originals
        # If this fails, we can just do the rest of the moves
        for region in self.cache.values():
            tmp_path = self.path / TMP_FORMAT.format(*region.coords)
            perm_path = tmp_path.parent / REGION_FORMAT.format(*region.coords)
            tmp_path.replace(perm_path)
        self._sync_directory()

        # Remove the phase 1 dotfile first so a failure between removals
        # leaves directory in a unique state
        phase_1_path.unlink()
        self._sync_directory()
        phase_2_path.unlink()
        # It's OK if the phase 2 dotfile doesn't get removed immediately.
        # sync'ing the directory is used for happens-before, not for proper
        # durability.

    def save_fast(self):
        """Save every region currently cached (like :meth:`save_all`).

        Prefer speed over correctness; do not provide any guarantees beyond
        those of the basic region caching system.

        """
        if self._atomic:
            raise RuntimeError('Cannot save_fast() inside an atomic block.')
        old_max = self.max_cache
        self.max_cache = 0
        self.max_cache = old_max

    @property
    def atomic(self):
        """Make the following operations atomic.

        Either every change made within the block will be saved to disk, or
        none of those changes are saved to disk.  This should not be confused
        with the other three `ACID`_ guarantees (particularly isolation).  The
        transaction is aborted if and only if an exception is raised (but see
        below).

        .. _ACID: http://en.wikipedia.org/wiki/ACID

        Can be used as a context manager or decorator::

            @dim.regions.atomic
            def atomic_function():
                # Things in here will happen atomically.

            with dim.regions.atomic:
                # Things in here will happen atomically

        In some circumstances, you may need to call :meth:`recover_atomic`.
        This is generally only necessary if the system crashed or lost power
        while actually saving regions to disk.  The method may roll back a
        partially-committed transaction to ensure atomicity, or it may
        complete the transaction.

        It is legal to call :meth:`save_all` while in this context.  Doing so
        creates a sort of "checkpoint"; if an exception is raised, the context
        rolls back to the last checkpoint.  There is an implicit checkpoint at
        the beginning of the context.

        Nested invocations are legal but have no effect.

        This consumes memory more aggressively than normal operations.  It
        ignores the :attr:`max_cache` attribute for the sake of correctness.

        .. warning::

            This is not the same as thread safety.  If you require thread
            safety, use explicit locking.  Multiple threads attempting to
            enter or exit the atomic context at the same time can cause data
            corruption, and the rest of the class is similarly unsafe for
            concurrent access.

        .. note::

            Atomicity is only guaranteed on systems where :func:`os.replace`
            is atomic and :func:`os.fsync` can be used on a directory.  Most
            POSIX-compliant systems should satisfy these requirements.
            Windows most likely fails the second and perhaps the first as
            well.  The Python implementation of :meth:`pathlib.Path.touch` may
            also require a working ``O_EXCL`` flag, which is known to be
            broken under some versions of NFS.  More generally, working on a
            network drive of any kind is questionable.

        """
        return _AtomicContext(self)

    def recover_atomic(self) -> bool:
        """Recover from a failure during :attr:`atomic` or :meth:`save_all`.

        Call this method if a system crash or other severe problem occurs
        while exiting an :attr:`atomic` block.  It is not necessary to call
        this method if the crash occurred while control was still inside the
        block.  The method should also be called if :meth:`save_all` raised an
        exception, even if it did so inside an atomic block.

        Return True if the changes were saved, False if the changes were
        rolled back.  Also return True if the Dimension is already in a
        "clean" state and recovery is unnecessary.

        .. warning::

            Do not call this method while a save is in progress.  Doing so
            will likely cause severe data corruption.  This rule applies
            regardless of which process is performing the save.
            :meth:`save_all` raises a :exc:`~.exceptions.ConcurrentError` to
            indicate that it believes a save cannot be safely made at the
            current time.  Calling this method will override that safety
            check.

        """
        phase_1_path = self.path / FIRST_DOTFILE
        phase_2_path = self.path / SECOND_DOTFILE
        phase_1_exists = phase_1_path.exists()
        phase_2_exists = phase_2_path.exists()
        logger.info('Repairing failed save_all()')
        if phase_1_exists and phase_2_exists:
            # We were in phase 2.  Just finish it.
            logger.info('Completing save')
            tmpfile_glob = self.path.glob(TMP_GLOB)
            for source in tmpfile_glob:
                # Slice off the '.tmp' extension, leaving the '.mca'
                destination = source.parent / source.stem
                logger.debug('Replacing %s with %s', destination, source)
                source.replace(destination)
            logger.info('Save completed; removing dotfiles')
            phase_1_path.unlink()
            phase_2_path.unlink()
            return True
        elif phase_2_exists and not phase_1_exists:
            # Phase 2 was complete, but the dotfile did not get removed
            logger.info('Save already succeded; removing %s', phase_2_path)
            phase_2_path.unlink()
            return True
        elif phase_1_exists and not phase_2_exists:
            # We were in phase 1.  Roll the operation back
            logger.info('Rolling back save')
            tmpfile_glob = self.path.glob(TMP_GLOB)
            for path in tmpfile_glob:
                logger.debug('Removing %s', path)
                path.unlink()
            logger.info('Save reverted; removing %s', phase_1_path)
            phase_1_path.unlink()
            return False
        else:
            # Neither dotfile exists; the directory is "clean"
            assert not phase_1_exists and not phase_2_exists
            logger.info('Directory is clean; nothing to do')
            return True

    @property
    def max_cache(self):
        """The number of regions to keep cached.

        An unlimited number of regions can be cached temporarily, but when
        :meth:`release` is called, only this many regions will be kept.

        If set to :obj:`None` or we are inside an :attr:`atomic` block, the
        :meth:`release` method does nothing, and the cache may grow
        arbitrarily large.

        Implicitly calls :meth:`release` when set.

        """
        return self._max_cache

    @max_cache.setter
    def max_cache(self, new_max_cache: int):
        if new_max_cache is None:
            self._max_cache = new_max_cache
            return
        new_max_cache = int(new_max_cache)
        if new_max_cache < 0:
            raise ValueError("max_cache must be nonnegative")
        self._max_cache = new_max_cache
        self.release()

    @property
    def cache_size(self):
        """Number of regions currently cached.

        Should be <= :obj:`max_cache` immediately after a call to
        :meth:`release`, except inside an :attr:`atomic` invocation.

        """
        return len(self.cache)

    def _load_region(self, r_x: int, r_z: int,
                     require_exist: bool=True) -> region.Region:
        """Load the given region from disk and return it.

        No caching.

        """
        region_path = self.path / REGION_FORMAT.format(r_x, r_z)
        try:
            region_file = region_path.open(mode='rb')
        except FileNotFoundError as err:
            if require_exist:
                raise IndexError('Region {}, {} does not exist'
                                 .format(r_x, r_z)) from err
            logger.info('Region %d, %d does not exist, generating empty',
                        r_x, r_z, exc_info=True)
            return region.Region(r_x, r_z, namespace=self._namespace)
        with region_file:
            return region.Region.load(r_x, r_z, region_file,
                                      namespace=self._namespace)

    def get_region(self, r_x: int, r_z: int,
                   require_exist: bool=True) -> region.Region:
        """Return the requested region.

        Looks for a file with a name like ``r.1.2.mca`` in :attr:`path`, and
        loads it using :meth:`.region.Region.load`.  If the region is cached,
        the cached copy is returned directly.

        """
        try:
            result = self.cache[r_x, r_z]
        except KeyError:
            result = self._load_region(r_x, r_z, require_exist)
            self.cache[r_x, r_z] = result
            return result
        self.cache.move_to_end((r_x, r_z))
        return result

    def flush_cache(self, *, save=True):
        """Trim the cache to at most :attr:`max_cache` items.

        If save is True, any regions discarded from the cache will be saved to
        disk (instead of just dropping them).

        """
        if self.max_cache is None:
            return
        if self._atomic:
            return
        while len(self.cache) > self.max_cache:
            coords, reg = self.cache.popitem(last=False)
            if save:
                r_path = self.path / TMP_FORMAT.format(*coords)
                with r_path.open(mode='wb') as output:
                    reg.save(output)
                r_path.replace(self.path / REGION_FORMAT.format(*coords))

    def release(self):
        """Equivalent to :meth:`flush_cache` with save=True."""
        self.flush_cache(save=True)

    def close(self):
        """Empty the cache and set :attr:`max_cache` to zero."""
        self.max_cache=0


class _EntitySliceable:
    def __init__(self, dim: Dimension):
        self.dim = dim

    def __repr__(self):
        return '<_EntitySliceable: owner={!r}>'.format(self.dim)

    @staticmethod
    def _slice_cleanup(idx):
        try:
            x_slice, y_slice, z_slice = idx
        except ValueError as ve:
            raise TypeError('Only 3D slicing allowed') from ve
        if any(s.step is not None for s in (x_slice, y_slice, z_slice)):
            raise ValueError('You may not specify a step')
        if any(s.start is None or s.stop is None for s in (x_slice, z_slice)):
            raise ValueError('Unbounded slicing in the X or Z dimension')
        y_slice = slice(*y_slice.indices(HEIGHT_LIMIT))
        return x_slice, y_slice, z_slice

    @staticmethod
    def _in_range(idx):
        return lambda ent: all(sl.start <= coord < sl.stop
                               for sl, coord in zip(idx, ent.pos))

    @_cache_correct
    def __getitem__(self, idx):
        x_slice, y_slice, z_slice = self._slice_cleanup(idx)
        idx = (x_slice, y_slice, z_slice)
        in_range = self._in_range(idx)
        x_range, _, z_range = self.dim._make_chunk_range(*idx)
        result = set()
        for c_x, c_z in itertools.product(x_range, z_range):
            ck = self.dim._getchunk(c_x, c_z)
            result.update(x for x in ck.entities
                          if in_range(x))
        return result

    @_cache_correct
    def __setitem__(self, idx, seq):
        x_slice, y_slice, z_slice = self._slice_cleanup(idx)
        idx = (x_slice, y_slice, z_slice)
        mapping = collections.defaultdict(set)

        seq = set(seq)

        # First, figure out which chunk each entity belongs to
        for ent in seq:
            x, y, z = ent.pos
            mapping[int(x)//CHUNK_BLOCKS, int(z)//CHUNK_BLOCKS].add(ent)

        in_range = self._in_range(idx)

        # Now, for each chunk...
        x_range, _, z_range = self.dim._make_chunk_range(x_slice,
                                                         y_slice,
                                                         z_slice)
        for c_x, c_z in itertools.product(x_range, z_range):
            ck = self.dim._getchunk(c_x, c_z)
            preexisting = (ent for ent in ck.entities
                           if not in_range(ent))
            # Attach all the entities belonging to that chunk, plus
            # already-present entities which were not in the range specified.
            # Start with the custom entities so they take precedence over
            # duplicates.
            # XXX: Not sure if this behavior of set.union() is contractual.
            ck.entities = mapping[c_x, c_z].union(preexisting)

    def __delitem__(self, idx):
        self.__setitem__(idx, set())

    def _flush_cache(self):
        return self.dim._flush_cache()


class _AtomicContext(contextlib.ContextDecorator):
    def __init__(self, owner: FileRegionManager):
        self.owner = owner
        self.stack = []

    def __repr__(self):
        return '<_AtomicContext: owner={!r}>'.format(self.owner)

    def __enter__(self):
        if self.owner._atomic:
            self.stack.append(False)
        else:
            self.owner.save_all()
            self.owner._atomic = True
            self.stack.append(True)

    def __exit__(self, exc_type, exc_value, traceback):
        if not self.stack.pop():
            return False
        if exc_type is None:
            self.owner.save_all()
        else:
            # Throw out the cache entirely
            self.owner.cache = collections.OrderedDict()
        self.owner._atomic = False
        self.owner.flush_cache(save=False)
        # Do not suppress exceptions
        return False
