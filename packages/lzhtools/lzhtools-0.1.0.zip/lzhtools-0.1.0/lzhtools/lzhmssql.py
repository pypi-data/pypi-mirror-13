#coding=utf-8
'''
Created on 2014年12月10日

@author: lizenghai

'''
from lzh.pub_func import *
import pymssql
import pandas as pd
import numpy as np


def gettradedate(conn):
    '''获取交易日
    返回一个只有1列的df类型数据。列名为'date'，内容为字符串。
    eg:gettradedate(conn)
    '''
    sqlstr= 'SELECT ALL [Date] FROM [AUTO].[dbo].[T_PROP_CAL] where DateOffFlag=0'
    cur = conn.cursor()
    cur.execute(sqlstr)
    a=pd.DataFrame(cur.fetchall(),columns=['date'])
    a.date=list(map(str2str,a['date']))
    if len(a) == 0:
        raise ValueError("{0}函数未能获取到交易日".format(gettradedate.__name__)) 
    return a


def getmarketdata(conn,collist,limitdate,tablename='T_DATA_DAYDATA'):
    '''获取全部市场行情
    eg:getmarketdata(conn)
    '''
    colsdict = {'id':'[UID]',
                'date':'[DateValue]',
                'sym':'[Contract]',
                'open':'[OpenPrice]',
                'high':'[HighPrice]',
                'low':'[LowPrice]',
                'close':'[ClosePrice]',
                'vol':'[Vol]',
                'openint':'[OpenInt]',
                'clearprice':"[ClearPrice]"
                }
    colstr=''
    for i in range(len(collist)):
        if i == 0:
            colstr = colsdict[collist[i]]
            continue
        if collist[i] not in colsdict.keys():
            print('cuowu')
        colstr += ','+colsdict[collist[i]]
        
    sqlstr='SELECT ALL {0} FROM [AUTO].[dbo].[{2}] where DateValue>{1}'.format(colstr,limitdate,tablename)
    cur = conn.cursor()
    cur.execute(sqlstr)
    a=pd.DataFrame(cur.fetchall(),columns=collist)
#    a.date=list(map(str2str,a['date']))
    if len(a) == 0:
        raise ValueError("{0}函数未能获取到市场行情".format(getmarketdata.__name__)) 
    return a

