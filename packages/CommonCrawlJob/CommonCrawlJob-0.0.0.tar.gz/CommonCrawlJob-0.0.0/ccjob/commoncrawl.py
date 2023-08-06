from boto.s3.key import Key
import boto

from mrjob.job import MRJob
from warc import WARCFile
from urllib import url2pathname

from . gzipstream import GzipStreamFile

__all__ = ['CommonCrawl']


class CommonCrawl(MRJob):

    dataset = boto.connect_s3(anon=True).get_bucket('aws-publicdatasets')

    def process_record(self, body):
        raise NotImplementedError()

    def mapper(self, key, line):

        warcfile = WARCFile(fileobj=GzipStreamFile(Key(self.dataset, line)))

        for record in warcfile:
            if record['Content-Type'] == 'application/http; msgtype=response':
                payload = record.payload.read()
                headers, body = payload.split('\r\n\r\n', 1)
                if 'Content-Type: text/html' in headers:
                    for value in self.process_record(body):
                        yield ((url2pathname(record.url), value), 1)

                    self.increment_counter('commoncrawl', 'processed_records', 1)

    def reducer(self, url, values):
        yield (url[0], url[1])
