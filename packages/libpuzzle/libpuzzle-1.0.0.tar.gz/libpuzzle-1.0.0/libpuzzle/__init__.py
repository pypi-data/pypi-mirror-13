from libpuzzle.bases import *
from libpuzzle.objects import Puzzle, Signature

from ._version import get_versions
__version__ = get_versions()['version']
del get_versions

__all__ = ['Puzzle',
           'PuzzleError',
           'Signature',
           'SIMILARITY_THRESHOLD',
           'SIMILARITY_HIGH_THRESHOLD',
           'SIMILARITY_LOW_THRESHOLD',
           'SIMILARITY_LOWER_THRESHOLD']
