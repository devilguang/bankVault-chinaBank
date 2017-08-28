#!/usr/bin/env python
# -*- coding: utf-8 -*-
import os
import datetime as dt
from PIL import Image, ImageDraw, ImageFont
import subprocess

#一个完整的演示
from whoosh.index import create_in  
from whoosh.fields import *  
from whoosh.analysis import RegexAnalyzer
import os, os.path, sys
import win32process, win32event
import pyodbc

# analyzer = RegexAnalyzer(ur"([\u4e00-\u9fa5])|(\w+(\.?\w+)*)")
# schema = Schema(title=TEXT(stored=True), path=ID(stored=True), content=TEXT(stored=True, analyzer=analyzer))
# ix = create_in("indexdir", schema)
# writer = ix.writer()
# writer.add_document(title=u"First document", path=u"/a", content=u"This is the first document we’ve added!")
# writer.add_document(title=u"Second document", path=u"/b", content=u"The second one 你 中文测试中文 is even more interesting!")
# writer.commit()
# searcher = ix.searcher()
#
# results = searcher.find("content", u"first")
# print results[0]
# results = searcher.find("content", u"你")
# print results[0]
# results = searcher.find("content", u"测试")
# print results[0]


# -----------python 调用外部EXE
# 方法一：
# command_str = r'D:\PDESetup\PDESetup\PDE\PDE.exe'+' '+r'F:\PycharmProjects\src\MPG36321SDD\DATA\CxrfWinc1.DB'
# p1 = subprocess.Popen(["cmd", "/C", command_str],stdout=subprocess.PIPE).communicate()[0]
# print p1
# 方法二：
#os.system(command_str)
# 方法三：
#os.startfile(r'D:\PDESetup\PDESetup\PDE\PDE.exe')


# 方法四：
exe_path = r'D:\PDESetup\PDESetup\PDE\PDE.exe'  # sys.argv[1]
exe_file = r'F:\PycharmProjects\src\MPG36321SDD\DATA\CxrfWinc1.DB'  # sys.argv[2]
# with open(exe_file,'r') as f:
#     l1 = f.readline()
#     print l1
#os.chdir(exe_path)

# try:
#     handle = win32process.CreateProcess(exe_path,
#             '', None, None, 0,
#             win32process.CREATE_NO_WINDOW,
#             None ,
#             exe_path,
#             win32process.STARTUPINFO())
#     running = True
# except Exception, e:
#     print "Create Error!",e
#     handle = None
#     running = False
#
# while running:
#         rc = win32event.WaitForSingleObject(handle[0], 1000)
#         if rc == win32event.WAIT_OBJECT_0:
#                 running = False
# #end while
# print "GoodBye"


# import sqlite3
# conn=sqlite3.connect(exe_file)
# ret=conn.execute("SELECT name from sqlite_master WHERE TYPE=\"table\"")
# print ret


# -*- coding: utf8 -*-
# import xlrd
#
# fname = "reflect.xls"
# bk = xlrd.open_workbook(fname)
# shxrange = range(bk.nsheets)
# try:
#     sh = bk.sheet_by_name("Sheet1")
# except:
#     print "no sheet in %s named Sheet1" % fname
# # 获取行数
# nrows = sh.nrows
# # 获取列数
# ncols = sh.ncols
# print "nrows %d, ncols %d" % (nrows, ncols)
# # 获取第一行第一列数据
# cell_value = sh.cell_value(1, 1)
# # print cell_value
#
# row_list = []
# # 获取各行数据
# for i in range(1, nrows):
#     row_data = sh.row_values(i)
#     row_list.append(row_data)

# from openpyxl import *
#
# wb = load_workbook(exe_file)
# print(wb.get_sheet_names())
# a_sheet = wb.get_sheet_by_name('Sheet1')
# # 获得sheet名
# print(a_sheet.title)
# # 获得当前正在显示的sheet, 也可以用wb.get_active_sheet()
# sheet = wb.active
# #
from pypxlib import Table
file = r'F:\PycharmProjects\src\MPG36321SDD\allData\DATA0524\CxrfWinc.DB'
table = Table(file)
print table
print len(table)
fs = table.fields
for f in fs:
    print f,

row = table[0]
#row = row[u'总编号']
#print row

try:
    for row in table:
        print row[u'批号']
finally:
    table.close()





# LOCATION = "C:\test"
#
# cnxn = pyodbc.connect(r"Driver={{Microsoft Paradox Driver (*.db )\}};DriverID=538;Fil=Paradox 5.X;DefaultDir={0};Dbq={0};CollatingSequence=ASCII;".format(LOCATION), autocommit=True, readonly=True)
# cursor = cnxn.cursor()
# cursor.execute("select last, first from test")
# row = cursor.fetchone()
# print row


import requests
from suds import WebFault
from suds.client import Client


def TestUrlOpen():
    url = "http://www.webxml.com.cn/WebServices/WeatherWebService.asmx/getWeatherbyCityName?theCityName=58367"
    page = requests.get(url)
    txt = page.text
    print txt
    # lines = page.readlines()
    # page.close()
    # document = ""
    # for line in lines:
    #     document = document + line.decode('utf-8')
    #
    # from xml.dom.minidom import parseString
    # dom = parseString(document)
    # strings = dom.getElementsByTagName("string")
    # print (strings[6].childNodes[0].data + " " + strings[7].childNodes[0].data)


def TestSuds():
    url = 'http://webservice.webxml.com.cn/WebServices/WeatherWS.asmx?WSDL'
    client = Client(url)
    print(client)
    print(client.service.getWeather('58367'))

if __name__ == '__main__':
    # TestUrlOpen()
    TestSuds()


