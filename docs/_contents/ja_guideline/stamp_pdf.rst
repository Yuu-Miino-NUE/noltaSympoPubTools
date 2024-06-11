.. _PdfStampTools: https://github.com/Yuu-Miino-NUE/PdfStampTools

原稿 PDF へのスタンピング
===================================

本パッケージは，原稿 PDF に対してロゴやページ番号をスタンプする機能を提供します．
関連する機能は，:mod:`.pdfTools` モジュールにまとめられています．

Overlay PDF の作成
----------------------

原稿 PDF にロゴや学会情報をスタンプするためには，スタンプ用の PDF ファイル（以下，Overlay PDF）を作成する必要があります．
別パッケージではありますが，PdfStampTools_ の
:func:`.put_logo_with_text` 関数を用いることで，ロゴ画像と学会情報を含む Overlay PDF を作成することができます．
PdfStampTools_ は，本パッケージと依存関係にありますので，追加でインストールする必要はありません．

.. literalinclude:: /py_examples/ex_put_logo_with_text.py
    :language: python

上記のプログラムによって，次のような Overlay PDF が出力されます．

.. image:: /_images/first_page_overlay.png
    :class: with-border
    :width: 50%
    :align: center


PDF スタンピング
----------------------

Overlay PDF を用意したら，原稿 PDF にスタンプを行います．
原稿 PDF は ``row_pdfs`` ディレクトリにまとめて保存されていると仮定します．
以下は，ディレクトリ構造の例です．

.. code-block:: bash

    row_pdfs
    └── 6000.pdf
    first_page_overlay.pdf

:func:`.stamp_all_pdfs` 関数を用いることで，全ての PDF にスタンプを行うことができます．
各 PDF の先頭ページには Overlay PDF をスタンプし，全てのページにページ番号を付与します．
スタンプ後の PDF ファイルは指定したディレクトリに保存します．
スタンプ後の PDF ファイル名は，セッションコードとセッションオーダ，発表順に基づいて決定されます．
``data.json`` については，:doc:`DB レコードの整形 <load_from_db>` を参照してください．

.. literalinclude:: /py_examples/ex_stamp_all_pdfs.py
    :language: python
    :lines: 1-9

元 PDF に対して，生成された PDF は，次のような形になります．

.. image:: /_images/ex_stamp.png
    :class: with-border
    :width: 100%
    :align: center

ページ番号の装飾は，:func:`.stamp_all_pdfs` 関数の ``encl`` 引数で指定できます．
デフォルトでは，``encl="en_dash"`` となっており，ハイフンで囲まれたページ番号が付与されます．

.. note::

    ページ番号の付与は，著者情報 JSON に保存されている順番で行われます．

.. hint::

    何かしらの要因で単一の PDF にスタンプを行いたい場合は，:func:`.stamp_single_pdf` 関数を使用してください．
    こちらの関数では開始ページを指定できます．

ページ番号の保存
----------------------

:func:`.stamp_all_pdfs` 関数は，ページ番号付与済みの :class:`.SessionList` オブジェクトを返します．
このオブジェクトを JSON ファイルとして保存することで，著者情報の JSON は完成します．

.. literalinclude:: /py_examples/ex_stamp_all_pdfs.py
    :language: python
    :lines: 11-

原稿 PDF の統合
----------------------

ページ番号が付与された PDF を全て統合し，fullvolume PDF を作成します．

.. literalinclude:: /py_examples/ex_merge_all_pdfs.py
    :language: python

