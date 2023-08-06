from libpuzzle.bases import Puzzle
from six import text_type

PICKLE_ATTRS = (
    'max_width',
    'max_height',
    'lambdas',
    'noise_cutoff',
    'contrast_barrier_for_cropping',
    'max_cropping_ratio',
    'autocrop'
)


class Puzzle(Puzzle):

    def __init__(self, **opts):
        """Initialize a new puzzle object.

        Parameters:
            max_width (int):
            max_height (int):
            lambdas (int):
            noise_cutoff (double):
            contrast_barrier_for_cropping (double):
            max_cropping_ratio (double):
            autocrop (bool):
        """
        self.max_width = opts.pop('max_width', 3000)
        self.max_height = opts.pop('max_height', 3000)
        self.lambdas = opts.pop('lambdas', 9)
        self.noise_cutoff = opts.pop('noise_cutoff', 2.0)
        value = opts.pop('contrast_barrier_for_cropping', 0.05)
        self.contrast_barrier_for_cropping = value
        self.max_cropping_ratio = opts.pop('max_cropping_ratio', 0.25)
        self.autocrop = opts.pop('autocrop', True)

    def from_filename(self, filename):
        """Load signature from filename

        Parameters:
            filename (str): filename
        Returns:
            Signature
        """
        if isinstance(filename, text_type):
            filename = filename.encode('utf8')
        value = self.fill_cvec_from_file(filename)
        return Signature(value, puzzle=self)

    def from_signature(self, value):
        """Load signature from value

        Parameters:
            value (bytes): the signature
        Returns:
            Signature
        """
        return Signature(value, puzzle=self)

    def from_compressed_signature(self, value):
        """Load signature from compressed value

        Parameters:
            value (bytes): the signature
        Returns:
            Signature
        """
        return Signature(None, puzzle=self, compressed=value)

    def __getstate__(self):
        return {attr: getattr(self, attr) for attr in PICKLE_ATTRS}

    def __setstate__(self, state):
        for attr in PICKLE_ATTRS:
            if attr in state:
                setattr(self, attr, state[attr])

    def __eq__(self, other):
        if isinstance(other, Puzzle):
            for attr in PICKLE_ATTRS:
                if getattr(other, attr) != getattr(self, attr):
                    return False
            return True


class Signature:

    def __init__(self, value, puzzle, compressed=None):
        if not value and not compressed:
            raise ValueError('value or compressed are required')
        self._value = value
        self._compressed = compressed
        self.puzzle = puzzle

    def __repr__(self):
        return '<%s(%s..)>' % (self.__class__.__name__, self.value[:5])

    def __eq__(self, other):
        if isinstance(other, Signature):
            # Only signatures can be compared
            return self.value == other.value \
                and self.compressed == other.compressed

    @property
    def value(self):
        if not self._value:
            self._value = self.puzzle.uncompress_cvec(self._compressed)
        return self._value

    @property
    def compressed(self):
        if not self._compressed:
            self._compressed = self.puzzle.compress_cvec(self._value)
        return self._compressed

    def distance(self, other):
        """Get the distance with another signature

        Parameters:
            other (Signature):
        Return:
            float
        """
        sign1 = self.value
        sign2 = other.value
        return self.puzzle.vector_normalized_distance(sign1, sign2)

    def __getstate__(self):
        return {
            'value': self._value,
            'compressed': self._compressed,
            'puzzle': self.puzzle
        }

    def __setstate__(self, state):
        self._value = state.get('value', None)
        self._compressed = state.get('compressed', None)
        self.puzzle = state.get('puzzle', None)
