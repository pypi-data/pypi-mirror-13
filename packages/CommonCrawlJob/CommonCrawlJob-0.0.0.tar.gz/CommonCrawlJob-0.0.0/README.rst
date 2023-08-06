Common Crawl Data Extraction
============================

Extract data from common crawl using elastic map reduce

    Note: This project uses Python 2.7.11

Setup
-----

To develop locally, you will need to install the ``mrjob`` Hadoop
streaming framework, the ``boto`` library for AWS, the ``warc`` library
for accessing the web data, and ``gzipstream`` to allow Python stream
decompress gzip files.

Use pip to install these libraries.

.. code:: sh

    $ pip install git+https://github.com/qadium-memex/CommonCrawlJob.git

Quick Start
-----------
Create a Google Analytics Extractor

.. code:: sh

   $ touch GoogleAnalytics.py

.. code:: python

    from cclib import CommonCrawl

    class GATagJob(CommonCrawl):

        def process_record(self, body):
            # Regular Expression for Google Analytics Tracker
            pat = re.compile(r"[\"\']UA-(\d+)-(\d)+[\'\"]")

            for match in pat.finditer(body):
                if match:
                    yield match.groups()[0]

            self.increment_counter('commoncrawl', 'processed_document', 1)


    if __name__ == '__main__':
        GATagJob.run()

Testing Locally
---------------

Generate WARC file

.. code:: sh

    $ ccjob --date=2015 2015.warc
    $ head -n 1  2015.warc > test.warc

Run the Google Analytics extractor locally

.. code:: sh

    $ python GoogleAnalytics.py -r local < test.warc


Region Configuration
--------------------

For best performance, you should launch the cluster in the same region
as your data

Common Crawl Region
-------------------
:S3: US Standard
:EMR: US East (N. Virginia)
:API: ``us-east-1``

Configuring ``mrjob.conf``
--------------------------

Make sure to download an EC2 Key Pair ``pem`` file for your map reduce
job and add it to the ``ec2_key_pair`` and ``ec2_key_pair_file``
variables.

Make sure that the ``PEM`` file has permissions set properly by running

.. code:: sh

    $ chown 600 $MY_PEM_FILE

.. code:: sh

   $ wget https://www.python.org/ftp/python/2.7.11/Python-2.7.11.tgz

.. code:: yaml

    runners:
      emr:
        aws_region: 'us-east-1'
        aws_access_key_id: <Your AWS_ACCESS_KEY_ID>
        aws_secret_access_key: <Your AWS_SECRET_ACCESS_KEY>
        cmdenv:
            AWS_ACCESS_KEY_ID: <Your AWS_ACCESS_KEY_ID>
            AWS_SECRET_ACCESS_KEY: <Your AWS_SECRET_ACCESS_KEY>
        ec2_key_pair: <Path to your PEM file>
        ec2_key_pair_file: <Name of the Key>
        ssh_tunnel_to_job_tracker: true
        ec2_instance_type: 'm1.xlarge'
        ec2_master_instance_type: 'm1.xlarge'
        emr_tags:
            project: 'Memex'
            name: 'CC-GoogleAnalytics'
        num_ec2_instances: 12
        ami_version: '2.4.10'
        python_bin: python2.7
        interpreter: python2.7
        bootstrap_action:
            - s3://elasticmapreduce/bootstrap-actions/install-ganglia
        upload_files:
            - CommonCrawl.py
        bootstrap:
            - tar xfz Python-2.7.11.tgz#
            - cd Python-2.7.11
            - ./configure && make && sudo make install
            - sudo python2.7 get-pip.py#
            - sudo pip2 install --upgrade pip setuptools wheel
            - sudo pip2 install -r requirements.txt#

Run on Amazon Elastic MapReduce
-------------------------------

First copy the ``mrjob.conf.template`` into ``mrjob.conf``

Note: > Make sure to fill out the necessary AWS credentials with your
information

.. code:: sh

    $ python GoogleAnalytics.py -r emr \
                                --conf-path="mrjob.conf" \
                                --output-dir="s3n://$S3_OUTPUT_BUCKET" \
                               data/arcindex.txt

