#coding=utf-8
'''
Config配置文件类
'''
import configparser

class Config:
    def __init__(self,path):
        '''Config类
        @params path:ini文件路径
        '''
        self.path = path
        self.config = configparser.ConfigParser()
        
    def getConfig(self,section, key, defaultvalue=''):
        '''
        #获取config配置信息。当未找到指定块下的键值时，返回默认值。
		@params section:块名
		@params key:键值
		@params defaultvalue:默认值
        '''
        self.config.read(self.path)
        if self.has_option(section, key):
            tmp = self.config.get(section, key)
        else:
            tmp = defaultvalue
        
        return tmp
    
    def setConfig(self,section, key,value):
        '''
        #写入config配置文件
        '''
        self.config.read(self.path)
        if not self.has_section(section):
            self.config.add_section(section) 
        self.config.set(section, key,value)
        return self.config.write(open(self.path, 'w'))
    def getSections(self):
        '''
        # 返回读取到的所有工作块
        '''
        return self.config.sections()
    def has_section(self,section):
        '''
        # check whether the section is exist
        '''
        return self.config.has_section(section)
    def has_option(self, section, option):
        '''
        # 检查section中是否存在option
        '''
        return self.config.has_option(section, option)
if __name__ == '__main__':
    print('atest')
    configfile = 'config1.ini'
    cn = Config(configfile)
    cn.setConfig('states333', 'lastcheckdate', '3')
    cn.setConfig('states2', 'lastcheckdate', '3')
    print(cn.getConfig('states', 'lastcheckdate'))
    print(cn.has_section('section'))
    print(cn.has_option('states333', 'lastcheckdate'))