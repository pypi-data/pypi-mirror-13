libpuzzle
=========


Implements libpuzzle_ for python.

It is designed to quickly find visually similar images (GIF, PNG, JPG), even
if they have been resized, recompressed, recolored or slightly modified.

Sample applications:

* finding duplicate images in photo libraries
* image classification
* image search services
* moderation (pictures sent by users on forums, wikis, blogs, etc). Pictures
  similar to other pictures that were previously banned can be signaled to
  moderators.

The library relies on the GD Library in order to load bitmap pictures.

Installation:

    pip install libpuzzle


Usage::

    from libpuzzle import Puzzle, SIMILARITY_THRESHOLD

    puzzle = Puzzle()
    sign1 = puzzle.from_filename('img1.jpg')
    sign2 = puzzle.from_filename('img2.png')
    distance = sign1.distance(sign2)
    if distance <= SIMILARITY_THRESHOLD:
        print('images are propably the same')

API:

.. py:data:: SIMILARITY_THRESHOLD
.. py:data:: SIMILARITY_HIGH_THRESHOLD
.. py:data:: SIMILARITY_LOW_THRESHOLD
.. py:data:: SIMILARITY_LOWER_THRESHOLD

.. py:class:: Puzzle

    .. py:attribute:: max_width

    .. py:attribute:: max_height

    .. py:attribute:: lambdas

    .. py:attribute:: noise_cutoff

    .. py:attribute:: p_ratio

    .. py:attribute:: contrast_barrier_for_cropping

    .. py:attribute:: max_cropping_ratio

    .. py:attribute:: autocrop

    .. py:method:: from_filename(filename) -> Signature

    .. py:method:: from_signature(sign) -> CompressedSignature

    .. py:method:: from_signature(sign) -> Signature

    .. py:method:: vector_normalized_distance(sign1, sign2) -> bool

.. py:class:: Signature

.. py:class:: CompressedSignature

.. py:exception:: PuzzleError

    Raise when something went wrong

.. _libpuzzle: https://www.pureftpd.org/project/libpuzzle
