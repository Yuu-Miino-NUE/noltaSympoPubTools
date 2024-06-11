.. _Epapers: https://mktg.epapers2.org/

DB レコードの整形
========================

本パッケージでは，データベース（以下，DB）から取得したレコード（論文情報一覧）を整形するためのユーティリティ関数を提供しています．
システム担当者から提供された DB レコード（Excel/CSV） を読み込み，JSON 形式に整形します．

CSV から JSON への変換
----------------------------

前提として，Epapers_ のシステムからエクスポートされた CSV ファイルを読み込み，JSON 形式に変換することを考えます．
:func:`.load_epapers_sheet` 関数を用いることで，CSV ファイルを読み込み，
得られる :class:`.SessionList` オブジェクトを :meth:`.dump_json` メソッドによって JSON 形式に変換することができます．

.. attention::

    仕様や取引先の変更により，CSV ファイルの形式が変わる可能性があります．
    特に，列名が変わると，:func:`.load_epapers_sheet` 関数が正しく動作しなくなります．
    その際は，以下のような対応が必要です．

    - :func:`.load_epapers_sheet` 関数の仕様に合わせて列名を変更する．
    - :class:`.SessionList` オブジェクトを生成できる独自の読み込み関数を作成する．

    :class:`.SessionList` オブジェクトさえ作成できれば，本パッケージの他の機能を利用することができます．

.. literalinclude:: /py_examples/ex_load_epapers_sheet.py
    :language: python

.. hint::

    :func:`.load_epapers_sheet` の ``tz_offset_h`` 引数は，タイムゾーンのオフセットを指定します．
    GMT からのオフセットを時間で指定することで，現地時間に変換することができます．
    日本の場合， ``tz_offset_h=9`` と指定します．

:meth:`.dump_json` によって出力される JSON ファイルは，以下のような形式になります．

.. literalinclude:: /py_examples/data.json
    :language: json

.. hint::

    ``pages`` が ``null`` となりますが，これは後でページ番号を付与するための項目ですので，気にしないでください．

.. SeeAlso::
    :mod:`.sheet2json`
        レコード整形関係のユーティリティ関数を提供するモジュール
    :func:`.load_epapers_sheet`
        セッション情報を読み込む関数
    :class:`.SessionList`
        セッション情報を保持するクラス
