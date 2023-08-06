"""A file wrapper which acts as a cache for on-demand evaluation of conversions.

This object is used in lieu of a file in order to allow the various importers to
reuse each others' conversion results. Converting file contents, e.g. PDF to
text, can be expensive.
"""
__author__ = 'Martin Blais <blais@furius.ca>'

import chardet

from beancount.utils import file_type


# Maximum number of bytes to read in order to detect the encoding of a file.
HEAD_DETECT_MAX_BYTES = 128 * 1024


class FileMemo:
    """A file memoizer which acts as a cache for on-demand evaluation of conversions.

    Attributes:
      name: A string, the name of the underlying file.
    """

    def __init__(self, filename):
        self.name = filename

        # A cache of converter function to saved conversion value.
        self._cache = {}

    def __str__(self):
        return '<FileWrapper filename="{}">'.format(self.name)

    def convert(self, converter_func):
        """Registers a callable used to convert the file contents.
        Args:
          converter_func: A callable which accepts a filename and produces some
          derived version of the file contents.
        Returns:
          A bytes object, with the contents of the entire file.
        """
        try:
            result = self._cache[converter_func]
        except KeyError:
            result = self._cache[converter_func] = converter_func(self.name)
        return result

    def contents(self):
        """An alias for reading the entire contents of the file."""
        return self.convert(contents)


def mimetype(filename):
    """A converter that computes the MIME type of the file.

    Returns:
      A converter function.
    """
    return file_type.guess_file_type(filename)


def contents(filename):
    """A converter that just reads the entire contents of a file.

    Args:
      num_bytes: The number of bytes to read.
    Returns:
      A converter function.
    """
    # Attempt to detect the input encoding automatically, using chardet and a
    # decent amount of input.
    rawdata = open(filename, 'rb').read(HEAD_DETECT_MAX_BYTES)
    detected = chardet.detect(rawdata)
    encoding = detected['encoding']

    # Ignore encoding errors for reading the contents because input files
    # routinely break this assumption.
    errors = 'ignore'

    with open(filename, encoding=encoding, errors=errors) as file:
        return file.read()


def head(num_bytes=8192):
    """A converter that just reads the first bytes of a file.

    Args:
      num_bytes: The number of bytes to read.
    Returns:
      A converter function.
    """
    def head_reader(filename):
        with open(filename) as file:
            return file.read(num_bytes)
    return head_reader
