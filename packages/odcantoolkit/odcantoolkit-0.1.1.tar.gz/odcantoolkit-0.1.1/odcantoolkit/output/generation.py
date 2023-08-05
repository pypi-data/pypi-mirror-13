import json
import re
from odcantoolkit.parser.abstract import AbstractParser

INT_REGEX = re.compile("^-?([0-9]\s?)+$")
FLOAT_REGEX = re.compile("^-?[0-9]+(\.)[0-9]+$")
MONEY_EN_REGEX = re.compile("^\$?[+-]?[0-9]{1,3}(?:,?[0-9]{3})*(?:\.[0-9]{2})?\$?$")
MONEY_FR_REGEX = re.compile("^\$?[+-]?[0-9]{1,3}(?:\s?[0-9]{3})*(?:\,[0-9]{2})?\$?$")


class JSONMaker:
    """Wrapper class to produce a JSON object or a JSON like dictionnary

    The object must be couple with an AbstractParser object to retrieve the
    data from the source file
    """

    def __init__(self, parser):
        if not isinstance(parser, AbstractParser):
            raise TypeError("parser parameters must be of type Parser")
        self._parser = parser
        self._headers = self._find_headers()

    def jsonify(self):
        """Returns a JSON object"""

        jsonObjects = self._build_json_dictionary()
        return json.JSONEncoder(ensure_ascii=False).encode(jsonObjects)

    def make_json_dictionary(self):
        """Returns a JSON like dictionnary"""

        jsonObjects = self._build_json_dictionary()
        return jsonObjects

    def _build_json_dictionary(self):
        """Returns a JSON like dictionnary

        Data is read item by item with the parser and formatted
        as a JSON object
        """

        jsonObjects = []
        for rawObject in self._parser:
            try:
                jsonObject = self._build_object(rawObject)
                jsonObjects.append(jsonObject)
            except AssertionError:
                pass
        return jsonObjects

    def _find_headers(self):
        """Query the parser to get the list of headers"""

        headers = self._parser.find_headers()
        stripped_headers = []
        for h in headers:
            stripped_headers.append(h.replace('.', ''))
        return stripped_headers

    def _build_object(self, rawObject):
        """Return a single dictionnary that reprensents a JSON object

        rawObject -- must be a list where each item represents a JSON object property
        """
        assert len(rawObject) == len(self._headers)
        jsonObject = {}
        for i in range(len(rawObject)):
            strippedStr = rawObject[i].strip()
            if INT_REGEX.match(strippedStr):
                strippedStr = strippedStr.replace(' ', '')
                strippedStr = strippedStr.replace(',', '')
                jsonObject[self._headers[i]] = int(strippedStr)
            elif MONEY_EN_REGEX.match(strippedStr):
                strippedStr = strippedStr.replace(',', '').replace('$', '')
                jsonObject[self._headers[i]] = float(strippedStr)
            elif MONEY_FR_REGEX.match(strippedStr):
                strippedStr = strippedStr.replace(',', '.').replace(' ', '')
                strippedStr = strippedStr.replace('$', '')
                jsonObject[self._headers[i]] = float(strippedStr)
            elif FLOAT_REGEX.match(strippedStr):
                strippedStr = strippedStr.replace(',', '.')
                jsonObject[self._headers[i]] = float(strippedStr)
            else:
                jsonObject[self._headers[i]] = rawObject[i]
        return jsonObject
