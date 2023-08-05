import csv
from odcantoolkit.parser.abstract import AbstractParser


class CsvParser(AbstractParser):
    """Parser class used to read from a csv file

    Must be constructed with the a path the file
    """

    def __init__(self, filename):
        self._open_file(filename)
        self._reader = self._build_csv_reader()
        self._headersLocated = False
        self._headersLocation = 0

    def find_headers(self, nbRowsToCheck=20):
        nbColumn = len(next(self._reader))
        self._file.seek(0)
        strategies = (self._search_headers_single_row, )
        (location, payload) = (None, None)
        for strategy in strategies:
            (location, payload) = strategy(nbRowsToCheck, nbColumn)
            if location is not None:
                self._headersLocated = True
                self._headersLocation = location
                return payload
        raise RuntimeError("Couldn't find headers in this csv file")

    def _build_csv_reader(self):
        """Return a csv reader object.

        The Sniffer module is used to detect the correct file delimiters
        """

        dialect = csv.Sniffer().sniff(self._file.read())
        self._file.seek(0)
        return csv.reader(self._file, dialect)

    def _search_headers_single_row(self, nbRowsToCheck, nbColumn):
        """Return a list of the headers.

        The strategy to find the headers is the find the first row wich headers
        each his column filled or the row with the most column filled
        """
        largestColumnFilled = 0
        largestRow = None
        rowLocation = 0
        for i in range(0, nbRowsToCheck):
            try:
                row = next(self._reader)
            except StopIteration:
                break

            nbColumnFilled = 0
            for column in row:
                column = column.strip()
                if column != '':
                    nbColumnFilled = nbColumnFilled + 1
            if nbColumnFilled == nbColumn:
                self._file.seek(0)
                return(i, row)
            elif nbColumnFilled > largestColumnFilled:
                largestColumnFilled = nbColumnFilled
                largestRow = row
                rowLocation = i
        self._file.seek(0)
        return (rowLocation, largestRow)

    def __iter__(self):
        if self._headersLocated:
            self._file.seek(0)
            for i in range(0, self._headersLocation + 1):
                next(self._reader)
        return self

    def __next__(self):
        data = next(self._reader)
        return data
