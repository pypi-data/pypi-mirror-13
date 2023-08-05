BYTE_TO_ENCODING_LUT = {b'\x8e': 'cp863',
                        b'\x91': 'cp863',
                        b'\x97': 'cp863',
                        b'\x87': 'cp863',
                        b'\x90': 'cp863',
                        b'\x8a': 'cp863',
                        b'\x80': 'cp863',
                        b'\x82': 'cp863',
                        b'\x85': 'cp863',
                        b'\x92': 'cp863',
                        b'\x88': 'cp863',
                        b'\xa0': 'cp863',
                        b'\xc0': 'latin_1',
                        b'\xe9': 'latin_1',
                        b'\xe7': 'latin_1',
                        b'\xc7': 'latin_1',
                        b'\xf9': 'latin_1',
                        b'\xe8': 'latin_1',
                        b'\xc9': 'latin_1',
                        b'\xc8': 'latin_1',
                        b'\xe0': 'latin_1',
                        b'\xea': 'latin_1',
                        b'\xca': 'latin_1'
                        }


def guess_encoding(filename):
    """Returns an encoding alias.

    The whole file is read as an utf8 file. If an exception is raised,
    we try to find the find the original enconding in the byte to alias lookup table.
    Since the only language possible are french and english, we can make a pretty good
    guess.
    """

    encodingType = 'utf_8'
    with open(filename, 'rb') as dummy:
        try:
            dummy.read().decode(encodingType)
        except UnicodeDecodeError as err:
            dummy.seek(err.args[2])
            try:
                byte = dummy.read(1)
                encodingType = BYTE_TO_ENCODING_LUT[byte]
            except KeyError:
                return 'latin_1'
    return encodingType
