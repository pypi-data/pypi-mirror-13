import sys

from io import BytesIO, StringIO

if sys.version_info[0] > 2:
    import csv
else:
    import unicodecsv as csv


def _load_csv(filename):
    with open(filename, 'rb') as f:
        data = f.read()

    if sys.version_info[0] > 2:
        f = StringIO(data.decode('utf8'))
    else:
        f = BytesIO(data)

    reader = csv.DictReader(f)
    return reader
