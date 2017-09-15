# coding=utf-8

import sys
import json
import os
from cx_Freeze import setup, Executable


name = "speech2s"
version = "0.2"
description = 'Speech to Scratch (Julius speech recognition)'
author = 'Hiroaki Kawashima'
url ='https://github.com/memakura/speech2s'

# 変更しない
upgrade_code = '{A7EBBD8F-79A3-47BA-B17E-A06AABDB603A}'

# ----------------------------------------------------------------
# セットアップ
# ----------------------------------------------------------------
shortcut_table = [
    ("DesktopShortcut",        # Shortcut
     "DesktopFolder",          # Directory_
     "speech2s",                    # Name
     "TARGETDIR",              # Component_
     "[TARGETDIR]speech2s.exe",# Target
     None,                     # Arguments
     None,                     # Description
     None,                     # Hotkey
     None,                     # Icon
     None,                     # IconIndex
     None,                     # ShowCmd
     "TARGETDIR",              # WkDir
    )
    ]

# Now create the table dictionary
msi_data = {"Shortcut": shortcut_table}

build_exe_options = {"packages": ['asyncio'],
                    "excludes": [],
                    "includes": [],
                    "include_files": [
                        'julius/julius.exe',
                        'julius/main.jconf',
                        'julius/am-gmm.jconf',
                        'julius/model/lang_m',
                        'julius/model/phone_m',
                        'images/',
                        '00scratch/',
                        'ThirdPartyLicenses.txt'
                    ]
}
#                    "compressed": True


bdist_msi_options = {'upgrade_code': upgrade_code,
                    'add_to_path': False,
                    'data': msi_data
}

options = {
    'build_exe': build_exe_options,
    'bdist_msi': bdist_msi_options
}

# exeの情報
base = None #'Win32GUI' if sys.platform == 'win32' else None
icon = 'images/icon_256x256.ico'

# exe にしたい python ファイルを指定
exe = Executable(script='speech2s.py',
                 targetName='speech2s.exe',
                 base=base,
                 icon=icon
                 )
#                 copyDependentFiles = True

# セットアップ
setup(name=name,
      version=version,
      author=author,
      url=url,
      description=description,
      options=options,
      executables=[exe]
      )
