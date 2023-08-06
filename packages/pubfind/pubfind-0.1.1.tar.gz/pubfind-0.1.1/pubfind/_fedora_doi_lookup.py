from __future__ import print_function
from __future__ import unicode_literals

import sys
import time

import requests

from requests.exceptions import ConnectionError
from requests.utils import quote

other_args = 'type=tuples&lang=itql&format=CSV&limit=5'

doi_lookup = """
select $object from <#ri>
where  $object
       <info:fedora/fedora-system:def/model#hasModel>
       <info:fedora/fedora-system:FedoraObject-3.0>
and    ($object <dc:relation> 'info:doi/{0}' or
        $object <dc:relation> 'info:doi/{1}' or
        $object <dc:relation> 'info:doi/{2}')
"""
session = None


def get_results(risearch_base_url, doi):
    global session

    itql_query = doi_lookup.format(doi, doi.lower(), doi.upper())
    if not session:
        session = requests.Session()
    url = risearch_base_url + '?' + other_args + '&query=' + quote(itql_query)
    r = None
    while not r:
        try:
            r = session.get(url)
        except ConnectionError:
            print('(connection error)', file=sys.stderr, end='')
            sys.stderr.flush()
            time.sleep(5)
            pass

    return r.text


def _extract_pids(csv):
    csv_lines = csv.splitlines()
    assert csv_lines[0] == '"object"'
    csv_lines = csv_lines[1:]
    prefix = 'info:fedora/'
    prefix_len = len(prefix)
    object_pids = [object_id[prefix_len:] for object_id in csv_lines]
    return object_pids


def get_doi_objects(risearch_base_url, doi):
    pids = _extract_pids(get_results(risearch_base_url, doi))
    return pids
