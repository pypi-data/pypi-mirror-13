#coding=utf-8

from setuptools import setup, find_packages
import codecs
import os
long_desc = """
lzh
===============

.. image:: https://badge.fury.io/py/lzh.png
    :target: http://badge.fury.io/py/lzh

* can be easily to convert most of the date time to a standard format or string format
* can be easily read a large number of CSV files to a dicttype
* easy to use as most of the data returned are pandas DataFrame objects
* can be easily saved as csv, excel or json files
* can be inserted into MSSQL or MySQL or Mongodb

Installation
--------------

    pip install lzh
    
Upgrade
---------------

    pip install lzh --upgrade
    
Quick Start
--------------

::

    from lzhtools.feed import ReadMarketCSVFiles
    
    ReadMarketCSVFiles(2)
    
return::

    ReadMarketCSVFiles.Market
    {'XX1':data(pandas.DataFrame),
    'XX2':data(pandas.DataFrame),
    ... ...
    'XXn':data(pandas.DataFrame)
    }
    
"""


setup(
    name           = 'lzhtools',
    version        = '0.1.0',
    py_modules     = ['lzhtools'],
    author         = 'lizenghai',
    author_email   = '860007600@qq.com',
    url            = 'http://www.ac3.cn',
    description='',
    long_description = long_desc,
    packages = ['lzhtools'],
    license='BSD',
    keywords=['China stock data','futures trade','Stock trade','backtesting'],
    classifiers=['Development Status :: 4 - Beta',
    'Programming Language :: Python :: 3.2',
    'Programming Language :: Python :: 3.3',
    'Programming Language :: Python :: 3.4',
    'Programming Language :: Python :: 3.5',
    'License :: OSI Approved :: BSD License'],
    )