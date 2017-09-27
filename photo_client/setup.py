# -*- coding: utf-8 -*-
from distutils.core import setup
import py2exe
from glob import glob
import os

# python setup.py py2exe
mfcdir='D:/Anaconda2-4.3/Anaconda2-4.3.1/Lib/site-packages/pythonwin'
mfcfiles = [os.path.join(mfcdir, i) for i in ["mfc90.dll", "mfc90u.dll", "mfcm90.dll", "mfcm90u.dll", "Microsoft.VC90.MFC.manifest"]]
data_files = [("Microsoft.VC90.MFC", mfcfiles),
              ('platforms', glob(r'D:\Anaconda2-4.3\Anaconda2-4.3.1\Library\plugins\platforms\qwindows.dll')),
              ('images', glob(r'G:\items\photo\images\*.*')),
              ("imageformats", glob(r'D:\Anaconda2-4.3\Anaconda2-4.3.1\Library\plugins\imageformats\*.dll'))]
setup(windows=[{"script":"photoGather.py",
                "icon_resources": [(1, r'logo16.ico'),
                                   (1, r'logo32.ico'),
                                   (1, r'logo64.ico'),
                                   (1, r'logo48.ico'),
                                   (1, r'logo128.ico'),
                                   (1, r'logo256.ico')]}],
      options={"py2exe":{"includes":["sip",'PyQt5.QtCore']}},
      data_files=data_files)
