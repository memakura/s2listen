# speech2s
Speech 2 Scratch (based on Julius)

Installer: https://github.com/memakura/speech2s/tree/master/dist

![speech2s](https://github.com/memakura/speech2s/blob/master/images/ScratchSpeechRecog.png)

## 必要なもの / Requirement
- Windows 10 (64bit) (Windows 7 や 8でも可?)
- Scratch 2 offline editor
- Python 3.5 (64bit) (pythonで直接実行する場合) **dist以下のインストーラを用いる場合は不要**
    - aiohttp (pip install aiohttp しておく)

## デモ
1. Scratch 2 (offline) を立ち上げる
1. 00scratch/speech2s_demo.sb2 を開く
1. Pythonの動くコマンドラインで speech2s.py を実行する : `python speech2s.py`

## 使い方
1. Scratch 2 を立ち上げる
1. [ファイル] をシフトクリックして実験的なHTTP拡張を読み込みを選ぶ
1. 00scratch/speech2s_JA.s2e を開く
1. speech2s.py を実行する

## 音響モデルげ言語モデルの差し替え
1. ./julius/model 内 のファイルを差し替える

----

## Demo
1. Run scratch 2 (offline)
1. Open 00scratch/speech2s_demo.sb2
1. Run speech2s.py from command line : `python speech2s.py`

## How to use
1. Run scratch 2
1. Shift-click the File menu and select "Import Experimental Extension"
1. Open 00scratch/speech2s_EN.s2e
1. Run speech2s.py

## Add/change htsvoices
1. Replace files in ./julius/model

----
## Notes
- Julius Dictation Kit 4.4 is used; see ThirdPartyLicenses.txt
- Asynchronous I/O (asyncio) HTTP server (aiohttp) is used
- To build .msi, run `python setup.py bdist_msi` with python 3.5 (64bit)

## License
- New BSD

