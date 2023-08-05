# encoding: UTF-8

'''
文件相关操作
Created on 2015年6月30日

@author: ssxm
'''
import os,glob


def scandir(startdir, target,files =None) :
	'''查找指定文件夹下的指定后缀的文件（含子文件夹）并返回文件列表
	@params startdir：文件路径 支持相对路径和绝对路径
	@params target：文件后缀 eg:.csv
	'''
	if files == None:
		files = []
	if startdir[-1] != '\\':
		startdir += '\\'
	localpath = startdir + os.sep + "*"
	mylist = glob.glob(localpath)
	for obj in mylist:
		if os.path.isfile(obj):
			(dirname, filename) = os.path.split(obj)
			(shortname, extension) = os.path.splitext(filename)
			if extension == target:
				files.append(obj)
		if os.path.isdir(obj):
			scandir(obj, target,files)
	return files


def checkpath(path):
	'''检查路径是否存在，若不存在则创建（支持多层路径）
	'''
	if os.path.exists(path):
		if os.path.isfile(path)==False:
			return path
		else:
			raise ValueError('文件夹创建失败，存在同名文件。')
	else:
		os.makedirs(path)
		return path
