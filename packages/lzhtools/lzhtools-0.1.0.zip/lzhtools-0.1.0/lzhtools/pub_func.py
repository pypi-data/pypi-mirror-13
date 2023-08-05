#coding=utf-8
'''
Created on 2014年12月10日

@author: lizenghai

'''
import re 
import datetime,time,xlrd
from openpyxl import Workbook
import functools
from lzh.lfile import *
import pymssql
from dateutil.parser import parse

def formatsym(symbol):
    # 根据交易记录获取品种代码，如ru000 - > RU
    if symbol[1].isalpha():
        return symbol[:2]
    else:
        return symbol[:1]
def MaxDrawDown(plist,flag='all'):
    '''求最大资金回落，返回值均为绝对值。
    @param plist:序列
    @return list 
    其中，
    list[0]为回撤绝对值
    list[1]为相较于回撤前的高点的回撤百分比 
    list[2]为回撤发生的bar 数
    list[3]为此次回撤的不盈利期bar
    '''
    plen = len(plist)
    relativeHigh = 0            # 相对高点
    thisretreat = 0             # 当前回撤
    huichebars = 0
    jieduanlow = 0
    nowinbars = 0
    outlist = [0,0,0,0]
    for i in range(plen):
        if i == 0:                          #第一根bar初始化数据
            relativeHigh = plist[i]
            huichebars = 0
            jieduanlow = plist[i]
            outlist = [0,0,0,0]
            continue
        if relativeHigh <= plist[i]:         #高点被刷新时，阶段低点、不盈利bar数被重置
            relativeHigh = plist[i]
            jieduanlow = plist[i]
            nowinbars = 0
            huichebars = 0
        else:                               # 高点未被刷新
            nowinbars += 1
            if jieduanlow >= plist[i]:      # 回撤过程中低点被刷新
                jieduanlow = plist[i]
                huichebars += 1
                if outlist[0] < relativeHigh - jieduanlow:
                    outlist[0] = round(relativeHigh - jieduanlow,3)
                    outlist[1] = round((relativeHigh - jieduanlow)/plist[0],3)
                    outlist[2] = huichebars
            if outlist[3] < nowinbars:
                outlist[3] = nowinbars
#         print(i,'=>',outlist,'|||',relativeHigh,jieduanlow)
    if flag =='all':
        return outlist
    else:
        return outlist[flag]

def MaxDrawDown__(plist):
    '''求最大资金回落，返回值均为绝对值。
    @param plist:序列
    @return list 
    其中，
    list[0]为回撤绝对值
    list[1]为相较于回撤前的高点的回撤百分比 
    list[2]为回撤发生的bar 数
    list[3]为此次回撤的不盈利期bar
    '''
    plen = len(plist)
    relativeHigh = 0            # 相对高点
    thisretreat = 0             # 当前回撤
    huichebars = 0
    jieduanlow = 0
    nowinbars = 0
    outlist = [0,0,0,0]
    for i in range(plen):
        if i == 0:                          #第一根bar初始化数据
            relativeHigh = plist[i]
            huichebars = 0
            jieduanlow = plist[i]
            outlist = [0,0,0,0]
            continue
        if relativeHigh <= plist[i]:         #高点被刷新时，阶段低点、不盈利bar数被重置
            relativeHigh = plist[i]
            jieduanlow = plist[i]
            nowinbars = 0
            huichebars = 0
        else:                               # 高点未被刷新
            nowinbars += 1
            if jieduanlow >= plist[i]:      # 回撤过程中低点被刷新
                jieduanlow = plist[i]
                huichebars += 1
                if outlist[0] < relativeHigh - jieduanlow:
                    outlist[0] = round(relativeHigh - jieduanlow,3)
                    outlist[1] = round((relativeHigh - jieduanlow)/plist[0],3)
                    outlist[2] = huichebars
            if outlist[3] < nowinbars:
                outlist[3] = nowinbars
#         print(i,'=>',outlist,'|||',relativeHigh,jieduanlow)

    return outlist
def str2dt_old(strdatetime,flag='date'):
    '''字符串日期转为python的datetime日期
    @param strdatetime: 标准格式'2014-01-01'
    @return: datetime可计算日期
    
     这里如果用正则替换出日期来！可以简化无数种情况！！！！！！！正则的匹配。一定要弄明白
    '''
    strdatetime = strdatetime.replace('/','-').replace('.','-')
    if ':' in strdatetime:
        flag = 'datetime'
    dictflag = {}
    dictflag['date'] = '%Y-%m-%d'
    #print(len(strdatetime),strdatetime)
    if len(strdatetime) == 8 and '-' not in strdatetime:
        flag='date'
        dictflag['date'] = '%Y%m%d'
    dictflag['datetime'] = '%Y-%m-%d %H:%M:%S'
    dictflag['time'] = '%H:%M:%S'
    adate = datetime.datetime.strptime(strdatetime,dictflag[flag])
    return adate

def str2dt(tmpdatetime,maybe=False):
    '''利用现行模块进行日期转换
    '''
    if tmpdatetime == '':
        return ''
    else:
        return parse(tmpdatetime,dayfirst=True)

def dt2str(dtdatetime,flag = "date"):
    '''日期时间型转为字符串格式
    @param1 dtdatetime: datetime
    @param2 flag:转换格式
				date：默认格式 '2015-01-01'
				datetime:'2015-01-01 11:10:55'
				time:'11:10'
				dtnum:20150101111055
				datenum:20150101
    '''
    dictformat = {}
    dictformat['date'] = "%Y-%m-%d"
    dictformat['datenum'] = "%Y%m%d"
    dictformat['datetime'] = "%Y-%m-%d %H:%M"
    dictformat['dtnum'] = "%Y%m%d%H%M"
    dictformat['time'] = "%H:%M"

    flag = flag.lower()
    if flag in dictformat.keys():
        if isinstance(dtdatetime, str):
            dtdatetime = str2dt(dtdatetime)
        tmp = dtdatetime.strftime(dictformat[flag])
    else:
        raise ValueError(dt2str.__name__+"中参数flag="+flag+"类型错误!") 
    return tmp

def str2str(tmp,flag='date'):
    
    tmp = str2dt(tmp,flag)
#    print("字符串转dt:",tmp)
    tmp = dt2str(tmp,flag)
#    print("dt转str:",tmp)
    return tmp
        
def str2str2(tmp,flag='date'):
    '''
    将日期时间转为标准日期时间
    @param tmp 日期时间字符串
    @param flag 转换格式   1、datetime 2、date 3、dt2d
    flag = datetime
    2014-5-1 9:04   --->    2014-05-01 09:04
    flag = date
    2014-5-1       --->    2014-05-01
    '''
    tmp = tmp.replace('/','-').replace('.','-')
    if flag.lower() == 'datetime':
        if len(tmp) == 19:
            try:
                tmp = time.strptime(tmp,"%Y-%m-%d %H:%M:%S")
            except:
                print('【日期时间】转换错误！')
        else:
            try:
                tmp = time.strptime(tmp,"%Y-%m-%d %H:%M")
            except:
                print('【日期时间】转换错误！')

        tmp = datetime.datetime(tmp[0],tmp[1],tmp[2],tmp[3],tmp[4])
        return tmp.strftime('%Y-%m-%d %H:%M')
    elif flag.lower() == 'date':
        if len(tmp) == 8:
            tmp = '-'.join([tmp[:4],tmp[4:6],tmp[6:]])
        try:
            tmp = tmp.split(' ')[0]
            tmp = time.strptime(tmp,"%Y-%m-%d")
        except:
            print('【日期】转换错误！')
            return -1
        tmp = datetime.datetime(tmp[0],tmp[1],tmp[2])        
        return tmp.strftime('%Y-%m-%d')
    elif flag.lower() == 'dt2d':
        try:
            tmp = time.strptime(tmp,"%Y-%m-%d %H:%M")
        except:
            print('【日期时间】转换错误！')
            return -2
        tmp = datetime.datetime(tmp[0],tmp[1],tmp[2],tmp[3],tmp[4])
        return tmp.strftime('%Y-%m-%d')



def exdt2str(aline):
    '''excel中的日期转为字符串日期
    '''
    thedt = aline[0]
    thedt = datetime.datetime(*xlrd.xldate_as_tuple(thedt,0))#x就是你那串数字的变量
    aline[0] = thedt.strftime("%Y-%m-%d")
    return aline


if __name__ == "__main__":
    #dt2str(datetime.datetime.now(),"date")
    a=str2str("20120101",'datetime')