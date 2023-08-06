# -*- coding: utf-8 -*-

from setuptools import setup, find_packages

setup(
    name='CommonCrawlJob',
    description='Extract data from common crawl using elastic map reduce',
    long_description='\n'.join(
        [
            open('README.rst', 'rb').read().decode('utf-8'),
        ]
    ),
    author='Qadium Inc',
    license='Apache Software License v2',
    url='https://github.com/qadium-memex/CommonCrawlJob',
    author_email='sang@qadium.com',
    include_package_data=True,
    packages=find_packages(exclude=['*tests']),
    version='0.0.0',
    zip_safe=False,
    entry_points={
        'console_scripts': [
            'ccjob = ccjob.__main__:main',
        ]
    },
    classifiers=[
        'Development Status :: 3 - Alpha',
        'Environment :: Console',
        'Intended Audience :: Developers',
        'Natural Language :: English',
        'License :: OSI Approved :: Apache Software License',
        'Operating System :: OS Independent',
        'Programming Language :: Unix Shell',
        'Programming Language :: Python',
        'Programming Language :: Python :: 2.7',
        'Topic :: Software Development :: Libraries :: Python Modules',
        'Topic :: Text Processing :: Linguistic',
        'Topic :: Utilities',
    ]
)
