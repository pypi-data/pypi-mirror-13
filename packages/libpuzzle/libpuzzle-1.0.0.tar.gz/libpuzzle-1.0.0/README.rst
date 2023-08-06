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

On a debian server, installation would be::

    $ apt -y install libpuzzle-dev libgd2-xpm-dev
    $ pip install libpuzzle


Usage::

    from libpuzzle import Puzzle, SIMILARITY_THRESHOLD

    puzzle = Puzzle()
    sign1 = puzzle.from_filename('img1.jpg')
    sign2 = puzzle.from_filename('img2.png')
    distance = sign1.distance(sign2)
    if distance <= SIMILARITY_THRESHOLD:
        print('images are propably the same')


API::

    SIMILARITY_THRESHOLD
    SIMILARITY_HIGH_THRESHOLD
    SIMILARITY_LOW_THRESHOLD
    SIMILARITY_LOWER_THRESHOLD

    class Puzzle:

        max_width  #

        max_height  #

        lambdas  #

        noise_cutoff  #

        p_ratio  #

        contrast_barrier_for_cropping  #

        max_cropping_ratio  #

        autocrop  #

        from_filename(filename) -> Signature
            # hydrate Signature from filename

        from_signature(sign) -> Signature
            # hydrate Signature from value

        from_compressed_signature(sign) -> Signature
            # hydrate Signature from compressed value


    class Signature:
        # Implements signature

        value  # the value
        compressed  # the compressed value

        distance(signature) -> float
            # distance between 2 signatures


    exception PuzzleError:
        # Raise when something went wrong

.. _libpuzzle: https://www.pureftpd.org/project/libpuzzle
