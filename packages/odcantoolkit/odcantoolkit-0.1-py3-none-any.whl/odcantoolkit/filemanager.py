import zipfile
import shutil
from os import path


def get_file_extension(filename):
    (root, ext) = path.splitext(filename)
    ext = ext.replace('.', '')
    return ext


def unzipfile(filepath, targetformat, outdir="."):
    """Returns name of the unzipped file

    Looks for the file matching the targetformat and unzip them
    filename -- Name of the file (str)
    targetformat -- Format to extract from the archive (CSV, HTML, etc)
    inspired by: stackoverflow.com/questions/4917284
    """

    extractedFiles = []
    with zipfile.ZipFile(filepath) as zip_file:
        for member in zip_file.namelist():
            filename = path.basename(member)

            if not filename:
                continue

            ext = get_file_extension(filename)
            if ext.upper() == targetformat.upper():
                source = zip_file.open(member)
                target = open(path.join(outdir, filename), 'wb')
                with source, target:
                    extractedFiles.append(filename)
                    shutil.copyfileobj(source, target)
    return extractedFiles


def handle_downloaded_file(filename, fileformat):
    dl_extension = get_file_extension(filename)
    names = [filename]
    if dl_extension.upper() != fileformat.upper():
        if dl_extension == "zip":
            names = unzipfile(filename, fileformat)
        else:
            print("Warning: The file format seems to be " +
                  "{0} and not {1}".format(dl_extension, fileformat) +
                  " (dataset might be wrongly labeled).")
    return names
