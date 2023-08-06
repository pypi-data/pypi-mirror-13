import gzip
import boto

from boto.s3.key import Key

try:
    from StringIO import StringIO
except ImportError:
    from io import StringIO

__all__ = (
    'get_crawl',
    'get_index',
    'get_buckets',
    'print_buckets',
)

DATASET = boto.connect_s3(anon=True).get_bucket('aws-publicdatasets')

def get_buckets():
    """
    By default get's the latest crawl prefix.

    Example:
    --------
    Get the latest crawl from 2014:

    .. code:: python

        >>> self.get_crawl(crawl_date='2014')

    :param crawl_date: str
        Crawl Date Prefix: EG. 2015-48

    :return: crawl_prefix
    :rtype: str
    """
    crawl_bucket = DATASET.list('common-crawl/crawl-data/', '/')
    return [
        key.name.encode('utf-8') for key in crawl_bucket if 'CC-MAIN' in key.name
    ]

def select_crawl(crawl_date=''):
    """
    Fuzzy match a common crawl crawl prefix from available s3 buckets.
    Always selects the latest crawl date matched.

    :param crawl_date: str
        Crawl date specifier

    :return: Selected crawl date
    :rtype: str

    """
    buckets = get_buckets()
    return max([i for i in buckets if crawl_date in i])

def get_index(prefix):
    """
    :param prefix: str
        Prefix to S3 bucket

    :return: Uncompressed warc index
    :rtype: str
    """
    botokey = Key(DATASET, prefix + 'warc.paths.gz')
    return gzip.GzipFile(fileobj=StringIO(botokey.read())).read()

def print_buckets():
    """
    Helper function to print out list of available buckets

    :return: Nothing is returned
    :rtype: None
    """
    print('Crawl Date Codes')
    for bucket in get_buckets():
        print(bucket.split('/')[-2].lstrip('CC-MAIN-'))
