from __future__ import print_function

from .__version__ import __version__, __build__
from . aws import select_crawl, get_index, print_buckets
from . redshift import gen_redshift_query

import sys

from argparse import ArgumentParser

def command_line():

    description = 'Helper tool to run MapReduce jobs over Common Crawl'
    version     = ' '.join([__version__, __build__])

    crawl_list = ArgumentParser(add_help=False)
    crawl_list.add_argument(
        '-l', '--list',
        action='store_true',
        help='Enumerate all possible crawl dates',
    )

    # Preparse Date Codes
    crawl, _ = crawl_list.parse_known_args()
    if crawl.list:
        print_buckets()
        exit(0)

    redshift_parser = ArgumentParser(add_help=False)
    redshift_parser.add_argument(
        '--redshift',
        'store_true',
    )

    cols, _ = redshift_parser.parse_known_args()
    if cols:
        print(gen_redshift_query(cols.redshift[0]))
        exit(0)

    parser = ArgumentParser(
        parents=[crawl_list, redshift_parser],
        prog='ccjob',
        description=description,
    )
    parser.add_argument(
        '-v', '--version',
        action='version',
        version="%s v%s" % ('ccjob', version)
    )
    parser.add_argument(
        '-d', '--date',
        nargs='?',
        default='latest',
        help='Specify crawl date',
        metavar='d',
    )
    parser.add_argument(
        '-f', '--file',
        nargs='?',
        metavar='f',
        default=None,
        help='Output to a file'
    )
    return parser.parse_args()

def main():
    args = command_line()
    crawl = select_crawl() if args.date == 'latest' else select_crawl(args.date)
    print(
        get_index(crawl),
        file=(open(args.file, 'wt') if args.file else sys.stdout),
        end='',
    )

if __name__ == '__main__':
    sys.exit(main())


