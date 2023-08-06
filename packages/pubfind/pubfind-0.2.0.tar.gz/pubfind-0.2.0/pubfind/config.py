# -*- coding: utf-8 -*-
"""Configuration module."""
from __future__ import absolute_import
from __future__ import unicode_literals

import sys

from logging import getLogger
from os.path import expanduser
from textwrap import dedent

import configargparse

__logs__ = getLogger(__package__)
_options = None


def get_parser():
    """Get config parser."""
    parser = configargparse.ArgParser(
        prog=__package__,
        usage='%(prog)s [options]',
        description=dedent(
            """
            pubfind looks for missing publications.
            """.rstrip()),
        default_config_files=['~/.pubfindrc', '.pubfindrc'])

    parser.add('-c', '--config', is_config_file=True,
               help='config file path')

    parser.add('--fedora-api', required=True,
               help='Fedora Commons API URL, usually https://.../fedora/')
    parser.add('--scopus-data', required=True,
               help='Scopus publications CSV data file')
    parser.add('--output-csv', help='Output CSV file', default='pubfind.csv')

    return parser


def get_options():
    """Get options."""
    global _options

    if not _options:
        parser = get_parser()

        pytest = sys.argv[0].endswith('/py.test')
        args = [] if pytest else None

        try:
            _options = parser.parse_args(args=args)
        except SystemExit:
            if pytest:
                __logs__.warning('failed to load options')
                return

            raise

        _options.scopus_data = expanduser(_options.scopus_data)
        _options.output_csv = expanduser(_options.output_csv)

    return _options
