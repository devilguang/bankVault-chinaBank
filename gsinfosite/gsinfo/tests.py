# encoding=UTF-8

import os
import win32api

import win32ui
import win32print
import win32con
#!/usr/bin/python3

from openpyxl import Workbook,load_workbook
from openpyxl.styles import Alignment, Font, Border, Side
import time
border = Border(left=Side(border_style='thin', color='FF000000'),
                    right=Side(border_style='thin', color='FF000000'),
                    top=Side(border_style='thin', color='FF000000'),
                    bottom=Side(border_style='thin', color='FF000000'),
                    outline=Side(border_style='thin', color='FF000000'),
                    vertical=Side(border_style='thin', color='FF000000'),
                    horizontal=Side(border_style='thin', color='FF000000')
                    )
template_path = u'G:\\items\\BullionCheckSys\\gsinfosite\\data\\template\\装箱清单.xlsx'
book = load_workbook(template_path)
sheet = book.worksheets[0]
# book = Workbook()
# sheet = book.active

sheet['A1'] = 56
sheet['A2'] = 43

now = time.strftime("%x")
sheet['A3'] = now

sub_area1 = sheet['A{0}:B{1}'.format(1, 2)]
for cs in sub_area1:
    for cell in cs:
        cell.border = border
book.save("sample.xlsx")
#
# def send_to_printer(title,txt):
#     hDC = win32ui.CreateDC()
#     hDC.CreatePrinterDC(win32print.GetDefaultPrinter())
#     hDC.StartDoc(title)
#     hDC.StartPage()
#     hDC.SetMapMode(win32con.MM_TWIPS)
#
#     ulc_x = 1000
#     ulc_y = -1000
#     lrc_x = 11500
#     lrc_y = -11500
#
#     hDC.DrawText(txt, (ulc_x, ulc_y, lrc_x, lrc_y), win32con.DT_LEFT)
#
#     hDC.EndPage()
#     hDC.EndDoc()
#
# def printer_win32api():
#     filename = r'C:\Users\Administrator\Desktop\aaa.xlsx'
#     print win32print.GetDefaultPrinter()
#     # win32api.ShellExecute(0,"print",filename,'/d:"%s"' % win32print.GetDefaultPrinter (),".",0)
#     # 第四个参数为None的时候使用默认的打印机
#
#
#
#
# if __name__ == "__main__":
#     # send_to_printer('123','123')
#     printer_win32api()