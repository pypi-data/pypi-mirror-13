
from setuptools import setup, find_packages
from codecs import open
from os import path

setup(
    name='batchly_api',

    version='0.7.2',

    description='Batchly API SDK for integration with the REST endpoint',
    long_description='Api for data integration with Batchly Platform',

    url='http://www.batchly.net',

    author='Batchly Support',
    author_email='support@batchly.net',

    license='MIT',

    classifiers=[
        'Development Status :: 5 - Production/Stable',

        'Intended Audience :: Developers',
        'Topic :: Internet :: WWW/HTTP :: Dynamic Content',

        'License :: OSI Approved :: MIT License',

        'Programming Language :: Python :: 2',
        'Programming Language :: Python :: 2.6',
        'Programming Language :: Python :: 2.7',
    ],

    keywords='batchly api sdk rest',

    packages=find_packages(exclude=['contrib', 'docs', 'tests']),

    install_requires=['Unirest>=1.1.6', 'jsonpickle>=0.7.1', 'poster>=0.8.1'],

)
