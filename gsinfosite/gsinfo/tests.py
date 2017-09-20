# encoding=UTF-8

import os
import win32api

import win32ui
import win32print
import win32con
from openpyxl import Workbook,load_workbook
from openpyxl.styles import Alignment, Font, Border, Side
import time

import zlib
import struct

def makeGrayPNG(data, height = None, width = None):
    def I1(value):
        return struct.pack("!B", value & (2**8-1))
    def I4(value):
        return struct.pack("!I", value & (2**32-1))
    # compute width&height from data if not explicit
    if height is None:
        height = len(data) # rows
    if width is None:
        width = 0
        for row in data:
            if width < len(row):
                width = len(row)
    # generate these chunks depending on image type
    makeIHDR = True
    makeIDAT = True
    makeIEND = True
    png = b"\x89" + "PNG\r\n\x1A\n".encode('ascii')
    if makeIHDR:
        colortype = 0 # true gray image (no palette)
        bitdepth = 8 # with one byte per pixel (0..255)
        compression = 0 # zlib (no choice here)
        filtertype = 0 # adaptive (each scanline seperately)
        interlaced = 0 # no
        IHDR = I4(width) + I4(height) + I1(bitdepth)
        IHDR += I1(colortype) + I1(compression)
        IHDR += I1(filtertype) + I1(interlaced)
        block = "IHDR".encode('ascii') + IHDR
        png += I4(len(IHDR)) + block + I4(zlib.crc32(block))
    if makeIDAT:
        raw = b""
        for y in xrange(height):
            raw += b"\0" # no filter for this scanline
            for x in xrange(width):
                c = b"\0" # default black pixel
                if y < len(data) and x < len(data[y]):
                    c = I1(data[y][x])
                raw += c
        compressor = zlib.compressobj()
        compressed = compressor.compress(raw)
        compressed += compressor.flush()
        block = "IDAT".encode('ascii') + compressed
        png += I4(len(compressed)) + block + I4(zlib.crc32(block))
    if makeIEND:
        block = "IEND".encode('ascii')
        png += I4(0) + block + I4(zlib.crc32(block))
    return png

def example():
    with open("cross3x3.png","wb") as f:
        f.write(makeGrayPNG([[0,255,0],[255,255,255],[0,255,0]]))

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
if __name__ == "__main__":
    # send_to_printer('123','123')
    # printer_win32api()
    example()