# speech2s
Speech 2 Scratch (Speech recognition for offline scratch 2 powered by Julius)

![speech2s](https://github.com/memakura/speech2s/blob/master/images/ScratchSpeechRecog.png)

## インストーラ版はこちら
Python のインストールが不要です．
- [インストールおよびブロックの使用方法，マイクの設定方法 (Wiki)](https://github.com/memakura/speech2s/wiki)
- [インストーラ (msiファイル) のダウンロード](https://github.com/memakura/speech2s/releases)

**以下では Python から実行する場合を説明します．Python をインストールせずに実行する場合は上のインストーラ版をお使いください．**

## 必要なもの / Requirement
- Windows 10 (64bit) (Windows 7 や 8でも可?)
- Scratch 2 offline editor
- Python 3.5 (64bit)
    - aiohttp (pip install aiohttp しておく)
- さらに，julius/model 以下の大きなファイルのダウンロードには [git lfs](https://git-lfs.github.com/) が必要

## デモ
1. Scratch 2 (offline) を立ち上げる
1. 00scratch/speech2s_demo.sb2 を開く
1. Pythonの動くコマンドラインで speech2s.py を実行する : `python speech2s.py`

## 使い方
1. Scratch 2 を立ち上げる
1. [ファイル] をシフトクリックして実験的なHTTP拡張を読み込みを選ぶ
1. 00scratch/speech2s_JA.s2e を開く
1. speech2s.py を実行する
1. オプション
    - `-m DNN` (音響モデルをDNNにする．デフォルトはGMM)
    - `-d (数字)` (マイク入力のデバイスを指定する: 何もオプションを指定せずに実行したときにはデフォルトのデバイスが選ばれる)
    - 指定できるデバイスは，julius が立ち上がる際に表示されるリストから選択可能
```
STAT: ###### initialize input device
[start recording]
Stat: adin_portaudio: audio cycle buffer length = 256000 bytes
Stat: adin_portaudio: sound capture devices:
  1 [MME: Microsoft サウンド マッパー - Input]
  2 [MME: マイク配列 (Realtek High Defini]
  3 [MME: ヘッドセット (SoundBuds Slim Ha]
  9 [Windows DirectSound: プライマリ サウンド キャプチャ ドライバー]
  10 [Windows DirectSound: マイク配列 (Realtek High Definition Audio)]
  11 [Windows DirectSound: ヘッドセット (SoundBuds Slim Hands-Free)]
```

## 音声入力デバイスの設定
- はじめて使う場合や認識がうまくいかないときは [Wiki/SetInputDevice.md](https://github.com/memakura/speech2s/wiki/SetInputDevice) を確認

## 音響モデルや言語モデルの差し替え
1. ./julius/model 内 のファイルを差し替える

## ライセンス
- 修正BSD
- Julius関連は ThridPartyLicenses.txt に従います．

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

## License
- New BSD
- See ThirdPartyLicenses.txt for Julius related files.

----
## Notes
- Julius Dictation Kit 4.4 is used; see ThirdPartyLicenses.txt
- Asynchronous I/O (asyncio) HTTP server (aiohttp) is used
- To build .msi, run `python setup.py bdist_msi` with python 3.5 (64bit)

