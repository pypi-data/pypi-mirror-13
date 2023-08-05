from odcantoolkit.parser.csv import CsvParser


class ParserFactory():
    """ Factory class to build parsers depending on the file type."""

    @staticmethod
    def build_csv_parser(filename):
        return CsvParser(filename)

    @staticmethod
    def build_parser(filetype, filename):
        if filetype.upper() == "CSV":
            return CsvParser(filename)
        else:
            raise NoParserFoundError("{0} file format is not supported".format(filetype))


class NoParserFoundError(Exception):
    def __init__(self, value):
        self.value = value

    def __str__(self):
        return repr(self.value)


def make_parser(fileformat, filename):
    """ Returns parser for the specified fileofmrat

    fileformat -- Format of the parsed file.
    filename -- Name of the parsed file.
    """
    parser = ParserFactory.build_parser(fileformat,
                                        filename)
    return parser
