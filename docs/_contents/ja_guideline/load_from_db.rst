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

.. literalinclude:: /py_examples/ex_load_epapers_sheet.py
    :language: python

上記のプログラムによって，CSV ファイルが読み込まれ，JSON ファイルが出力されます．

.. hint::

    :func:`.load_epapers_sheet` の ``tz_offset_h`` 引数は，タイムゾーンのオフセットを指定します．
    GMT からのオフセットを時間で指定することで，現地時間に変換することができます．
    日本の場合， ``tz_offset_h=9`` と指定します．

.. attention::

    仕様や取引先の変更により，CSV ファイルの形式が変わる可能性があります．
    特に，列名が変わると，:func:`.load_epapers_sheet` 関数が正しく動作しなくなります．
    その際は，以下のような対応が必要です．

    - :func:`.load_epapers_sheet` 関数の仕様に合わせて列名を変更する．
    - :class:`.SessionList` オブジェクトを生成できる独自の読み込み関数を作成する．

    :class:`.SessionList` オブジェクトさえ作成できれば，本パッケージの他の機能を利用することができます．


なお，:meth:`.dump_json` によって出力される JSON ファイルは，以下のような形式になります．

.. literalinclude:: /py_examples/data.json
    :language: json

JSON に含まれているデータの構造は，:class:`.Session` オブジェクトの属性に対応しています．
なお，``pages`` が ``null`` となりますが，ページ番号は DB 上に存在しないためです．後の工程で，ページ番号を付与します．

.. TODO: 工程へのリンク

.. attention::

    CSV から JSON への変換は，DB 上のデータが変更される毎に実行する必要があります．
    その度にページ番号の情報が失われるため，注意が必要です．

.. seealso::
    :mod:`.sheet2json`
        レコード整形関係のユーティリティ関数を提供するモジュール
    :func:`.load_epapers_sheet`
        セッション情報を読み込む関数
    :class:`.SessionList`
        セッション情報を保持するクラス

JSON の手動アップデート
---------------------------------------

投稿〆切後の修正依頼や，LaTeX で使用できない文字の置換のために，JSON ファイルを手動で修正することがあります．
その際は，以下のような手順で修正を行います．

.. literalinclude:: /py_examples/ex_update_sessions.py
    :language: python

ここで，``update.json`` は，データの修正パッチであり，以下のような形式になります．

.. literalinclude:: /py_examples/update.json
    :language: json
    :caption: update.json

``update.json`` では，以下の必須項目に基づいてレコードを検索し，その他の項目を修正します．

.. list-table::
    :header-rows: 1

    * - 必須項目
      - 説明
    * - ``category``
      - セッションのカテゴリ
    * - ``category_order``
      - カテゴリ内での順番
    * - ``papers.id``
      - Paper ID

なお，この例では，修正後のファイルとして ``updated_data.json`` が出力されますが，
:func:`.update_sessions` の ``overwrite`` 引数を ``True`` にすることで，元のファイルを上書きすることも可能です．

.. seealso::
    :func:`.update_sessions`
        セッション情報を更新する関数