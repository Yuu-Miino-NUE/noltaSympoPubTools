.. _Epapers: https://mktg.epapers2.org/

DB レコードの整形
========================

本パッケージでは，データベース（以下，DB）から取得したレコード（論文情報一覧）を整形するためのユーティリティ関数を提供しています．
システム担当者から提供された DB レコード（Excel/CSV） を読み込み，JSON 形式に整形します．

CSV から JSON への変換
----------------------------

前提として，Epapers_ のシステムからエクスポートされた CSV ファイルを読み込み，JSON 形式に変換することを考えます．
:func:`.load_epapers_sheet` 関数を用いることで，CSV ファイルを読み込みます．

.. literalinclude:: /py_examples/ex_load_epapers_sheet.py
    :language: python
    :lines: 1-6

``tz_offset_h`` 引数は，タイムゾーンのオフセットを指定します．
GMT からのオフセットを時間で指定することで，現地時間に変換することができます．
日本の場合， ``tz_offset_h=9`` と指定します．

その他の引数は，:func:`.load_epapers_sheet` 関数の仕様を参照ください．

生成された :class:`.SessionList` オブジェクトは，セッション情報を保持します．
セッションの保存順序は，デフォルトではセッションコード，オーダに基づきますが，``sort_session`` 引数に
任意のソート関数を指定できます．
セッションの保存順序は :doc:`stamp_pdf` のページ番号付与に影響します．


.. attention::

    仕様や取引先の変更により，CSV ファイルの形式が変わる可能性があります．
    特に，列名が変わると，:func:`.load_epapers_sheet` 関数が正しく動作しなくなります．
    その際は，以下のような対応が必要です．

    - :func:`.load_epapers_sheet` 関数の仕様に合わせて列名を変更する．
    - :class:`.SessionList` オブジェクトを生成できる独自の読み込み関数を作成する．

    :class:`.SessionList` オブジェクトさえ作成できれば，本パッケージの他の機能を利用することができます．


:class:`.SessionList` オブジェクト の :meth:`.dump_json` により，オブジェクトを JSON 形式で保存できます．

.. literalinclude:: /py_examples/ex_load_epapers_sheet.py
    :language: python
    :lines: 8-

保存した JSON ファイルは，以下のような形式になります．

.. literalinclude:: /py_examples/data.json
    :language: json

JSON に含まれているデータの構造は，:class:`.Session` オブジェクトの属性に対応しています．
なお，``pages`` が ``null`` となりますが，ページ番号は DB 上に存在しないためです．
ページ番号は :doc:`stamp_pdf` で付与します．

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