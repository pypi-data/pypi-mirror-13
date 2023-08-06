# -*- coding: utf-8  -*-
from __future__ import unicode_literals

from warnings import warn

from csl_data import LooseCslDataItem

TYPE_MAPPING = {
    'book chapter': 'chapter',
    'editorial': 'chapter',
    'article': 'article-journal',
    'note': 'article-journal',
    'letter': 'article-journal',
    'erratum': 'article',
    'article in press': 'article-journal',
    'conference paper': 'paper-conference',
}


class CSVProcessor(object):

    def __init__(self, csv):
        self.csv = csv

    def __iter__(self):
        for row in self.csv:
            item = LooseCslDataItem()

            eid = row['EID']
            assert eid

            item.EID = eid
            item.title = row['Title']

            doi = row['DOI'] or None

            if doi:
                item.DOI = doi.lower()

            if 'ISSN' in row:
                issn = row['ISSN']
                if issn:
                    item.ISSN = issn[:4] + '-' + issn[4:]

            volume = row['Volume'] or None
            if volume:
                item.volume = volume

            year = row['Year']
            if not year:
                warn('eid %s/doi %s doesnt have a year' % (eid, doi))
            item.year = year

            document_type = row['Document Type']
            assert document_type

            item.scopus_document_type = document_type

            document_type = document_type.lower()
            item_type = TYPE_MAPPING.get(document_type, document_type)

            item.type = item_type

            if 'Authors with affiliations' in row:
                authors_raw = row['Authors with affiliations']
            else:
                authors_raw = row['Authors']

            authors_split = authors_raw.split('; ')

            authors = []
            item.author = []
            for author in authors_split:
                author_parts = author.split(', ')
                author = {
                    'family': author_parts[0],
                    'given': author_parts[1],
                    'affiliation': ', '.join(author_parts[2:]),
                }
                authors.append(author)
            item.author = authors

            if 'Abstract' in row and row['Abstract']:
                abstract = row['Abstract'].strip()

                if abstract == '[No abstract available]':
                    pass
                elif '©' in abstract:
                    c_pos = abstract.index('©')
                    item.abstract_copyright = abstract[c_pos+1:].strip()
                    item.abstract = abstract[:c_pos].strip()
                else:
                    item.abstract = abstract

            if 'Author Keywords' in row and row['Author Keywords']:
                item.author_keywords = row['Author Keywords'].split('; ')
            if 'Index Keywords' in row and row['Index Keywords']:
                item.index_keywords = row['Index Keywords'].split('; ')

            yield item
