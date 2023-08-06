import unittest

from pubfind._fedora_doi_lookup import get_doi_objects


class DOITest(unittest.TestCase):

    def test_une_valid(self):
        url = 'https://e-publications.une.edu.au/fedora/risearch'
        doi = '10.1080/03004430.2013.875539'
        pids = get_doi_objects(url, doi)
        assert pids == ['une:18767']

    def test_une_invalid(self):
        url = 'https://e-publications.une.edu.au/fedora/risearch'
        doi = '10.1/1.2.3'
        pids = get_doi_objects(url, doi)
        assert pids == []
