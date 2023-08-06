gazeru
======

ニコ動からマイリスト単位で指定してダウンロードしてきて音声データだけ抽出して指定されたディレクトリに保存します。

installation
============

2系のサポートしてません ## ffmpeg, swftools のインストール 省略

pip で gazeru をインストール
----------------------------

::

    pip install gazeru

usage
=====

init でニコニコ動画のログイン情報とダウンロード先のディレクトリを指定

::

    $ gazeru init niconico_user niconico_password download_directory

http://www.nicovideo.jp/mylist/6280579

をダウンロードしたい場合 add で URL の末尾の数字を渡す

::

    $ gazeru add 6280579

pull でダウンロードが開始

::

    $ gazeru pull

その他

::

    $ gazeru -h
