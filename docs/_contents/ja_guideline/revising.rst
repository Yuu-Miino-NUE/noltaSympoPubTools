原稿の体裁チェック
==========================

本パッケージでは，原稿の体裁チェックを支援するため，以下の関数を提供しています．
体裁チェックそのものは，原稿の内容を理解している人間が行う必要がありますが，
以下の仕組みを利用することで，体裁チェック後の行程を効率化することができます．

チェック項目の策定
----------------------------

例えば，NOLTA'2023 では原稿が以下の項目に該当しないかをチェックし，
該当の場合には著者にメッセージを送信していました．

.. list-table::
   :header-rows: 1

   * - 項目キー
     - 送信メッセージ
   * - ORCID_NO_IDS
     - Some/all of the authors have not provided their ORCID iDs. Ensure that all authors ``must`` prepare the iDs and insert them in the correct format. The format includes the ORCID icon images and the hyperlinks to the personal page on the ORCID website, not only the ORCID iDs.
   * - ORCID_NO_LINK
     - Some/all of the authors have not inserted the hyperlink of the ORCID iDs.
   * - ORCID_INVALID_ICON
     - Some/all of the authors have not included the ORCID icon images with their ORCID iDs. All ORCID iDs must be referred to the correct format.
   * - ORCID_INVALID_FORMAT
     - All ORCID iDs are not in the correct format. They must be located at the end of the first column as a footnote; notice that they should not use the margin space when the authors update the paper. Our guidelines also request only the ORCID iDs in the manuscript but not their URLs. Instead of directly writing the URLs, please only insert the ORCID iDs with the URL hyperlinks.
   * - ONE_COLUMN
     - The manuscript must be in two columns.
   * - CC_OVERLAP
     - All manuscripts must keep the margins. The bottom margin of the manuscript is insufficient. This should cause some overlappings with publication stamps like page numbers, etc.
   * - MS_NO_A4_FORMAT
     - This manuscript is not A4 format. Please use the MS word template file in our official website.
   * - LATEX_NO_A4_FORMAT
     - This manuscript is not A4 format. Please use the LaTeX style file in our official website.
   * - OVERFLOW_MARGIN
     - All manuscripts must keep the margins. The equation or figure in the manuscript has broken the margin. Please refer to the extra message for detail.
   * - ORCID_EXTRA_COMMA
     - List of ORCID iDs include unnecessary comma and colon. Please check the LaTeX command usage for the iDs.
   * - ADOBE_OPEN_ERROR
     - Adobe Acrobat Reader cannot open the file.

チェック項目は以下のようにスプレッドシートで管理しておくと扱いやすいです．

.. image:: /_images/revise_err_msg.png
   :width: 100%

.. Note::

    チェック項目を追加・削除・修正する場合は，スプレッドシートを修正してください．:ref:`後々<err_msg>` に CSV としてエクスポートします．
    ただし，後述する ``EXTRA_COMMNETS`` 項目は，システムの予約語ですので，使用しないでください．


スプレッドシートでのチェック作業
--------------------------------------------

実際のチェック作業は，スプレッドシートの行を投稿論文のファイル名，列をチェック項目に対応させて行います．
体裁チェックの際にはロゴ・ページ番号をスタンプ済みの PDF ファイルを使用しますので，ファイル名は「A3L-33.pdf」のようになります．
下図を参照ください．

.. image:: /_images/revise_sheet.png
   :width: 100%

.. hint::

    複数名でダブルチェックを行い，一つのファイルに統合することで，ミスを防ぎます．

例外項目
--------------------------------------------

チェック項目には該当しないものの，修正を依頼したい点については，``EXTRA_COMMNETS`` 列に記載します．

.. image:: /_images/revise_extra_comments.png
    :width: 100%


スプレッドシートの出力
--------------------------------------------

``revise_sheet.csv``
~~~~~~~~~~~~~~~~~~~~~~~~

体裁チェックに利用したスプレッドシートは CSV 形式で出力しておきます．
この CSV を用いて，修正依頼メールを作成します．

.. literalinclude:: /py_examples/revise_sheet.csv
    :caption: revise_sheet.csv

.. caution::
    上記の ``revise_sheet.csv`` は，ダミーデータです．実際のデータは，スプレッドシートからエクスポートしてください．

.. _err_msg:

``err_msg.csv``
~~~~~~~~~~~~~~~~~~~~

チェック項目と対応する送信メッセージの一覧も CSV 形式で出力しておきます．

.. literalinclude:: /py_examples/err_msg.csv
    :caption: err_msg.csv
