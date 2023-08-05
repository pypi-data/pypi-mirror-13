import argparse
import sys
from odcantoolkit import prompt


class CliInterface():
    """Class to wrap the command interface option's

    The subcommand pattern is inspired by:
    http://chase-seibert.github.io/blog/2014/03/21/python-multilevel-argparse.html
    """

    @staticmethod
    def start_program():
        parser = argparse.ArgumentParser(
#            usage='''odcantoolkit <command> [args]

#Available commands are:
#    json    Fecth a dataset and creates JSON file
#    mongo   Fetch a dataset and inserts it in MongoDB'''
        )
        parser.add_argument('command', help='Command to run')
        args = parser.parse_args(sys.argv[1:2])

        if not hasattr(CliInterface, args.command):
            raise RuntimeError("No command found")

        getattr(CliInterface, args.command)()

    @staticmethod
    def _init_common_arguments(argparser):
        """Inits command line arugments for the script
        Returns argparser object
        """
        argparser.add_argument("--fileformat",
                               help="File format to fetch. Default is CSV")
        argparser.add_argument("id", help="ID to fetch from open.canada.ca")


    @staticmethod
    def json():
        """Starts main program with json mode argument list."""
        argParser = argparse.ArgumentParser()
        CliInterface._init_common_arguments(argParser)
        args = argParser.parse_args(sys.argv[2:])
        prompt.main(jsonmode=True, args=argParser.parse_args(sys.argv[2:]))

    @staticmethod
    def mongo():
        """Starts main program with mongo mode argument list. """
        argParser = argparse.ArgumentParser()
        argParser.add_argument("--dbname", help="Database name. Default is db",
                               default="db")
        argParser.add_argument("--collection", help="Collection name. Default is ckan",
                               default="ckan")
        argParser.add_argument("--host", help="Database url. Default is localhost",
                               default="localhost")
        argParser.add_argument("--port", help="Database port. Default is 27017",
                               default=27017, type=int)
        CliInterface._init_common_arguments(argParser)
        prompt.main(jsonmode=False, args=argParser.parse_args(sys.argv[2:]))
