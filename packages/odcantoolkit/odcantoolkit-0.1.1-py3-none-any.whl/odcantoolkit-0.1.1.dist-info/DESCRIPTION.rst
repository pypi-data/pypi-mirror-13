odcantoolkit - Open Data Canada Toolkit
=======================================

Overview
--------

odcantoolkit is a command line tool used to fetch datasets directly from
`Canada's open data portal <http://open.canada.ca/>`__. The data is then
converted to JSON format and can be loaded directly into a MongoDB
database.

Currently supported file formats: \* CSV

Installation
------------

The script can be simply installed via pip

::

    pip install odcantoolkit

Usage
-----

**JSON mode**

::

    odcantoolkit json [--filetype FILETYPE] id

The id is taken from a dataset's URL. To fecth
`this <http://open.canada.ca/data/en/dataset/4deb7637-3613-4012-84a2-882b06ab7458>`__
dataset, the command would be :

::

    odcantoolkit json 4deb7637-3613-4012-84a2-882b06ab7458

**MongoDB mode**

::

    odcantoolkit mongo [-h] [--fileformat FILEFORMAT [FILEFORMAT ...]]
                        [--dbname DBNAME] [--collection COLLECTION] [--host HOST]
                        [--port PORT]
                        id


