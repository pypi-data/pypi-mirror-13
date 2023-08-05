from csv import Error
from os import path
from sys import exit
import json
import urllib.error

from odcantoolkit.CKAN.CKAN_API import make_package_show_request, download_file
from odcantoolkit.output.generation import JSONMaker
from odcantoolkit.parser.factory import make_parser
from odcantoolkit.parser.factory import NoParserFoundError
from odcantoolkit.database.mongodb import IMongoDB
from odcantoolkit import filemanager
from pymongo.errors import ServerSelectionTimeoutError
from bson.errors import InvalidDocument


def printChoices(files):
    """Returns the choosen fileInfo object.

    files -- CKAN_API.FileInfo object list
    """
    print("\nChoose wich file to download: ")
    print("Warning: English versions should be prefered due to parsing issues.\n")
    limit = len(files)
    for i in range(0, limit):
        print("\t {0}. {1} ( {2} ) : {3}".format(i+1, files[i].get_name(),
                                                 files[i].get_language(),
                                                 files[i].get_format()))
    print("")
    (choice, quit) = (None, False)
    while quit is False and choice is None:
        choice = input("Enter file number to download (or q to quit): ")
        if choice.lower() == 'q':
            quit = True
        else:
            try:
                choice = int(choice)
                assert(choice > 0 and choice <= limit)
            except:
                print("Invalid choice.")
                choice = None
    return None if quit else files[choice - 1]


def error_and_exit(msg):
    print(msg)
    exit()


def mongodb_mode(jsonmaker, args):
    """Build JSON and send data to the database

    jsonmaker -- JSONMaker object to extract json data from
    args -- CLI arguments containing database connection information
    """
    (host, port, dbname, collection) = (args.host,
                                        args.port,
                                        args.dbname,
                                        args.collection)
    db = IMongoDB(dbname, collection, host, port)
    data = jsonmaker.make_json_dictionary()
    print("Connecting to database...")
    try:
        db.insert(data)
    except ServerSelectionTimeoutError:
        error_and_exit("Cannot reach the database. Make sure MongoDB is up and running.")
    except InvalidDocument:
        error_and_exit("The JSON produced is not formatted correctly. ")
    except:
        error_and_exit("Unknown error while trying to reach the database.")
    print("The data was successfully inserted the database.")


def json_mode(jsonmaker, filename):
    """Builds JSON and outputs it to a file

    jsonmaker -- JSONMaker object to extract json data from
    filename -- Name of the output file
    """
    jsonData = jsonmaker.make_json_dictionary()
    with open(filename, 'w') as outfile:
        json.dump(jsonData, outfile)
    print("{0} successfully created.".format(filename))


def main(jsonmode, args):
    print("Sending request to open.canada.ca...")
    try:
        fileInfos = make_package_show_request(args.id, args.fileformat)
    except urllib.error.HTTPError as err:
        error_and_exit("The requested package is not currently available ({0})".format(err))
    except urllib.error.URLError as err:
        error_and_exit("Coudn't reach the webserver. Verify internet connection. ".format(err))
    except RuntimeError:
        error_and_exit("The ID is not valid.")

    if len(fileInfos) <= 0:
        error_and_exit("Couldn't find any files matching the format requierements.")

    choosenFile = printChoices(fileInfos)
    if choosenFile is None:
        return

    print("\nDownloading requested file...")
    filename = download_file(choosenFile)
    print("Download successful.")
    files_name = filemanager.handle_downloaded_file(filename, choosenFile.get_format())

    if len(files_name) <= 0:
        error_and_exit("Cannot find the requested file in the zip archive")

    for f in files_name:
        try:
            parser = make_parser(choosenFile.get_format(), f)
        except NoParserFoundError as err:
            error_and_exit("Cannot parse the selected file format.")
        except:
            error_and_exit("Cannot parse the selected file." +
                           "Please manually verify this file's content.")

        try:
            jsonmaker = JSONMaker(parser)
        except Error:
            error_and_exit("Cannot parse the selected file." +
                           "Please manually verify this file's content.")

        ext = filemanager.get_file_extension(f)
        jsonFileName = path.basename(f).replace(ext, "json")
        json_mode(jsonmaker, jsonFileName) if jsonmode else mongodb_mode(jsonmaker, args)
