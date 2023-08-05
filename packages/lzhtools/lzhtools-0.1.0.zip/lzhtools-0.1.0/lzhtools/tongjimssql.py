#coding=utf-8
'''
Created on 2015年07月17日

@author: lizenghai

'''
import pymssql
import pandas as pd
from lzh.pub_func import *


class lzhmssql:
    def __init__(self,server,dbuser,pw,dbname):
        self.conn = pymssql.connect(host=server, user=dbuser,password=pw,\
        database=dbname,charset="UTF-8")            # 数据库连接
        
    def gettradedate(self):
        '''获取交易日
        返回一个只有1列的df类型数据。列名为'date'，内容为字符串。
        eg:gettradedate(conn)
        '''
        sqlstr= 'SELECT ALL [Date] FROM [AUTO].[dbo].[T_PROP_CAL] where DateOffFlag=0 '
        cur = self.conn.cursor()
        cur.execute(sqlstr)
        a=pd.DataFrame(cur.fetchall(),columns=['date'])
        a.date=list(map(str2str,a['date']))
        if len(a) == 0:
            raise ValueError("{0}函数未能获取到交易日".format(gettradedate.__name__)) 
        return a
    
    def getprice(self,sym,mydate,mykey):
        '''获取数据库中指定品种指定日期的指定价格
        '''
        pricekey = {'open':'OpenPrice','high':'HighPrice','low':'LowPrice','close':'ClosePrice'}
        mydate = dt2str(str2dt(mydate),'datenum')
        sqlstr="SELECT [{0}] FROM [AUTO].[dbo].[T_DATA_DAYDATA]  where DateValue = {1} and Contract = '{2}'".format(pricekey['open'],mydate,sym.upper())
        cur = sqlconn.cursor()
        cur.execute(sqlstr)
        a = cur.fetchall()
        print(a)
        if len(a)>1 or len(a)==0:
            raise ValueError("{0}函数运行出错！".format(getprice.__name__)) 
        
        return a[0][0]


if __name__ == '__main__':
    db = lzhmssql('192.168.1.53\hctfdb', 'sa','1234567', 'AUTO')
    
    tradedate = db.gettradedate()
    print(type(tradedate),tradedate)
    a = list(tradedate[tradedate['date']>'2015-01-01']['date'])
    print(a[0])
    dir = r'F:\SpyderWorkSpace\FuturesQuanyi\分表交易记录.xlsx'
    #pd.read_excel(io)