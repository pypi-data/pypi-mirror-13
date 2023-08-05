#coding=utf-8
'''
Created on 2013年11月28日
各类指标
@author: ssxm
'''
def Summation(source,length):
    SumValue = 0
    slen = len(source)
    if slen < length:
        SumValue = sum(source)
        return SumValue
    SumValue = sum(source[-1-length+1:])
    return SumValue

def ma(source,length):
    """ 计算移动平均线
        @param source 源数组
        @param length 均线跨度
        @return 移动平均序列
    """
    slen = len(source)
    rev = [0] * slen
    for i in range(slen):
        if i == 0 :
#             rev[i] = source[0]
            continue
        if i < length-1:
#             rev[i] = source[i]
            continue
        rev[i] = Summation(source[i-length+1:i+1], length) / length
        rev[i] = round(rev[i],3)
    return rev



def Highest(source,length):
    ''' 计算N周期内最高值
        @param source 源数组
        @param length 时间跨度
        @return N周期最高价序列
    '''
    if(len(source) < 1):
        # 序列中不存在数据，则返回空list
        return []    
    slen = len(source)
    rev = [999999] * slen
    if slen < length:
        return rev
    for i in range(slen):
        if i < length:
            tmp = list(source[:i+1])
        else:
            tmp = list(source[i-length+1:i+1])
        rev[i] = max(tmp)
#     rev = source[0:length] + rev[length-1:-1]
#     rev = [source[0]] + rev[0:-1]
    return rev
 
def Lowest(source,length):
    ''' 计算N周期内最低值
        @param source 源数组
        @param length 时间跨度
        @return N周期最低价序列
    '''
    if(len(source) < 1):
        return []    
    slen = len(source)
    rev = [0] * slen
    if slen < length:
        return rev
    for i in range(slen):
        if i < length:
            tmp = list(source[:i+1])
        else:
            tmp = list(source[i-length+1:i+1])
        rev[i] = min(tmp)
#     rev = [source[0]] + rev[0:-1]
    return rev

def MaxDrawDown(plist):
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
    return outlist

def AvgPrice(oo,hh,ll,cc):
    
    klen = len(oo)
    AvgPriceValue = [0] * klen
    for i in range(klen):
        if oo[i] >0:
            AvgPriceValue[i] = (cc[i] + oo[i] + hh[i] + ll[i]) * 1/4
        else:
            AvgPriceValue[i] = (cc[i] + hh[i] + ll[i]) * 1/3
    return AvgPriceValue
if __name__ =='__main__':
    a = list(range(1,10))
    print(a,'a')
#     sa=Summation(a,2)
#     print(sa,'Summation')
    print(ma(a,4),'ma2')
    b = [11,10,22,10,30,10,20,5,2,23,33,6,77,123,11,66]
    print(b)
    print(Highest(b,4))
    print(b)
    print(Lowest(b,4))
    