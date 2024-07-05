.. _国際会議メタデータ仕様書: https://www.ieice.org/jpn/books/pdf/metadata.pdf
.. _電子情報通信学会 NOLTA ソサイエティ: https://www.ieice.org/nolta/
.. _電子情報通信学会の Web サイト: https://www.ieice.org/jpn_r/about/kitei/conference.html

イントロダクション
===================

本パッケージについて
---------------------------

:mod:`noltaSympoPubTools` は，`電子情報通信学会 NOLTA ソサイエティ`_ が主催する国際シンポジウム NOLTA の出版物について，その作成を支援する目的で構成された Python パッケージです．
対象となる出版物は，以下の通りです．

- シンポジウムの Proceedings
- シンポジウムの Abstract Collection
- 原稿 PDF（ロゴやページ番号などの情報付与）

.. note::

    Proceedings や Abstract Collection は，本パッケージによって直接自動生成される訳ではありません．
    本パッケージは，データベース上の各種データを含む「中間ファイル」を自動生成し，出版物の作成を支援します．

その他，本パッケージは以下の機能を提供します．

- 原稿修正依頼メールの一括作成・送信（SMTP にのみ対応）
- 学会へ提出するメタデータの自動生成（国際会議メタデータ仕様書_ に基づきます）

準備物
----------------

本パッケージを利用するためには，以下の準備物が必要です．

.. list-table::
    :header-rows: 1
    :class: req-table

    * - ファイル名
      - 原稿 PDF 生成
      - TeX ソースファイル生成
      - 原稿修正リクエスト
      - 学会提出メタデータ
      - 提供／自作
      - 関連ページ
    * - | ``db_dump.csv``
        | ``<paper_id>.pdf``
      - ✓
      - ✓
      - ✓
      - ✓
      - 提供
      - :ref:`dbcsvjson`
    * - ``logo.png``
      - ✓
      -
      -
      -
      - 提供
      - :ref:`overlay`
    * - ``ss_organizers.json``
      -
      - ✓
      -
      - ✓
      - **自作**
      - :ref:`sso_json`
    * - ``err_msg.csv``
      -
      -
      - ✓
      -
      - **自作**
      - :ref:`err_msg`
    * - ``revise_sheet.csv``
      -
      -
      - ✓
      -
      - **自作**
      - :ref:`revise_sheet`
    * - ``metadata_*.csv``
      -
      -
      -
      - ✓
      - 提供
      - `電子情報通信学会の Web サイト`_
    * - ``common.json``
      -
      -
      -
      - ✓
      - **自作**
      - :ref:`common_csv`
    * - ``awards.json``
      -
      -
      -
      - ✓
      - **自作**
      - :ref:`metadata_article`