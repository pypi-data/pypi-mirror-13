# -*- coding: utf-8 -*-
"""
Created on Tue Nov 10 20:54:54 2015

@author: lizenghai
"""
from lzh.pub_func import *
import logging
logfile = r'.\log\run_{0}.log'.format(dt2str(datetime.datetime.now(),'dtnum'))
logging.basicConfig(level=logging.DEBUG,
                    format='%(asctime)s %(filename)s[line:%(lineno)d] %(levelname)s %(message)s',
                    datefmt='%a, %d %b %Y %H:%M:%S',
                    filename=logfile,
                    filemode='w')
#filename='.\\log\\run_{0}.log'.format(dt2str(datetime.datetime.now(),'dtnum')
#logging.debug('This is debug message')
#logging.info('This is info message')
#logging.warning('This is warning message')