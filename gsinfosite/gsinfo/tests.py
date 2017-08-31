# encoding=UTF-8

import os
import win32api

import win32ui
import win32print
import win32con


def send_to_printer(title,txt):
    hDC = win32ui.CreateDC()
    hDC.CreatePrinterDC(win32print.GetDefaultPrinter())
    hDC.StartDoc(title)
    hDC.StartPage()
    hDC.SetMapMode(win32con.MM_TWIPS)

    ulc_x = 1000
    ulc_y = -1000
    lrc_x = 11500
    lrc_y = -11500

    hDC.DrawText(txt, (ulc_x, ulc_y, lrc_x, lrc_y), win32con.DT_LEFT)

    hDC.EndPage()
    hDC.EndDoc()

def printer_win32api():
    filename = r'C:\Users\Administrator\Desktop\aaa.xlsx'
    print win32print.GetDefaultPrinter()
    # win32api.ShellExecute(0,"print",filename,'/d:"%s"' % win32print.GetDefaultPrinter (),".",0)
    # 第四个参数为None的时候使用默认的打印机




if __name__ == "__main__":
    # send_to_printer('123','123')
    printer_win32api()