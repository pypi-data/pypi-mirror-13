from abc import ABCMeta, abstractmethod
from odcantoolkit.encoding import guessing


class AbstractParser(metaclass=ABCMeta):
    """ Abstract class for any new file parser """

    def __init__(self):
        self.file_ = None

    @abstractmethod
    def find_headers(self):
        """Return a list of the file columns names """
        pass

    @abstractmethod
    def __iter__(self):
        pass

    @abstractmethod
    def __next__(self):
        """Returns a list representing the next element in the source file"""
        pass

    def __del__(self):
        self._close_file()

    def _open_file(self, filename):
        encodingType = guessing.guess_encoding(filename)
        self._file = open(filename, encoding=encodingType, errors='replace')

    def _close_file(self):
        if not self._file.closed:
            self._file.close()
