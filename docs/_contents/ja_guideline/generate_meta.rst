.. _国際会議メタデータ仕様書: https://www.ieice.org/jpn/books/pdf/metadata.pdf
.. _電子情報通信学会の Web サイト: https://www.ieice.org/jpn_r/about/kitei/conference.html

メタデータの自動生成
=======================

本パッケージでは， 国際会議メタデータ仕様書_ に基づいて，メタデータを自動生成する機能を提供しています．
メタデータは，以下の 3 点のファイルとして出力されます．

.. list-table::
    :header-rows: 1

    * - ファイル名
      - 内容
    * - ``metadata_common.csv``
      - シンポジウムの情報を記載した CSV ファイル
    * - ``metadata_session.csv``
      - セッションの情報を記載した CSV ファイル
    * - ``metadata_article.csv``
      - 論文の情報を記載した CSV ファイル

それぞれのファイルにはテンプレートがあります．詳しくは `電子情報通信学会の Web サイト`_ をご確認ください．

.. _common_csv:

``metadata_common.csv`` の生成
---------------------------------

まず，必要な情報を JSON 形式で保存します．必要な情報については :class:`.CommonInfo` クラスを参照してください．

.. literalinclude:: /py_examples/common.json
    :language: json
    :caption: common.json

次に，関数 :func:`.load_meta_common` を用いて，``common.json`` の内容を読み出します．

.. literalinclude:: /py_examples/ex_load_meta_common.py
    :language: python
    :lines: 1-3

.. note::
    :func:`.load_meta_common` 関数は，``common.json`` に保存された情報を読み込み，学会に提出可能なフォーマットに置き換えて返します．
    必要な情報が不足している場合，エラーが発生します．

最後に，ファイル名を指定して CSV をダンプします．``common_template.csv`` は `電子情報通信学会の Web サイト`_ からダウンロードできます．

.. literalinclude:: /py_examples/ex_load_meta_common.py
    :language: python
    :lines: 5-

以上により，学会に提出可能な ``metadata_common.csv`` が生成されます．

``metadata_session.csv`` の生成
---------------------------------

セッションのメタデータを自動生成するには，下記の 3 点の JSON ファイルが必要です．

.. list-table::
    :header-rows: 1

    * - ファイル名
      - 内容
      - データ型
      - 関連ページ
    * - ``data.json``
      - セッションの詳細
      - :class:`.Session`
      - | :ref:`dbcsvjson`
        | :ref:`save_page`
    * - ``ss_organizers.json``
      - SS オーガナイザ
      - :class:`.SSOrganizer`
      - :ref:`sso_json`
    * - ``common.json``
      - 学会共通情報
      - :class:`.CommonInfo`
      - :ref:`common_csv`

準備が整ったら，関数 :func:`.load_meta_sessions` を用いて，各セッションのメタデータを読み出し，CSV としてダンプします．

.. literalinclude:: /py_examples/ex_load_meta_sessions.py
    :language: python

以上により，学会に提出可能な ``metadata_session.csv`` が生成されます．

.. _metadata_article:

``metadata_article.csv`` の生成
---------------------------------

論文のメタデータを自動生成するには，下記の 2 点の JSON ファイルが必要です．

.. list-table::
    :header-rows: 1

    * - ファイル名
      - 内容
      - データ型
      - 関連ページ
    * - ``data.json``
      - セッションの詳細
      - :class:`.Session`
      - | :ref:`dbcsvjson`
        | :ref:`save_page`
    * - ``awards.json``
      - 受賞情報
      - :class:`.Award`
      - :ref:`metadata_article`

``awards.json`` は，以下のような形式で作成します．詳しくは :class:`.Award` クラスを参照してください．

.. literalinclude:: /py_examples/awards.json
    :language: json
    :caption: award.json

準備が整ったら，関数 :func:`.load_meta_articles` を用いて，各論文のメタデータを読み出し，CSV としてダンプします．

.. literalinclude:: /py_examples/ex_load_meta_articles.py
    :language: python

以上により，学会に提出可能な ``metadata_article.csv`` が生成されます．