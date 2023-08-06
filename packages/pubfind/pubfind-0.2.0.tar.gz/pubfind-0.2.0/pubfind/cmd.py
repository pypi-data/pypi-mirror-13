from __future__ import print_function
from __future__ import unicode_literals

import codecs
import sys

from pubfind.config import get_options
from pubfind.utils import _load_csv
from pubfind._fedora_doi_lookup import get_doi_objects
from pubfind._scopus_csv import CSVProcessor


def main():
    options = get_options()

    risearch_base_url = options.fedora_api + '/risearch'
    csv = _load_csv(options.scopus_data)

    counter = 0

    missing_pubs = []

    for item in CSVProcessor(csv):
        if not item.DOI:
            continue

        counter += 1

        object_pids = get_doi_objects(risearch_base_url, item.DOI)
        if not object_pids:
            missing_pubs.append(item)
            print('-', end='')
        else:
            print('.', end='')
        sys.stdout.flush()

    print('!', end='\n')

    output_file = open(options.output_csv, 'w')

    with codecs.open(options.output_csv, 'w', 'utf8') as output_file:
        output_file.write('EID,DOI,Document Type,Cited by,Title\n')

        for item in missing_pubs:
            csv_title = item.title.replace('"', '\\"')
            output_file.write('%s,%s,%s,%s,"%s"\n'
                              % (item.EID,
                                 item.DOI,
                                 item.scopus_document_type,
                                 item.scopus_citation_count,
                                 csv_title))
    print('%s written' % options.output_csv)
