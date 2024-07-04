原稿修正のリクエスト
============================

本パッケージでは，原稿修正のリクエストを支援する関数を提供しています．
関連するサブモジュールは :mod:`.requestRevise` および :mod:`.handleEmail` です．

.. _err_dict:

チェック項目と修正メッセージの読込
------------------------------------------

体裁チェック時に利用した :ref:`チェック項目<err_msg>` を ``dict`` 型で読み出します．

.. literalinclude:: /py_examples/ex_err_sheet2dict.py
    :language: python

チェックリストの読込と統合
------------------------------------------

体裁チェック時に :ref:`出力したチェックリスト CSV<revise_sheet>` を読み出します．
この際，:ref:`data.json<dbcsvjson>` を利用して，著者メタデータと紐つけます．
また，:ref:`err_dict` で得た ``dict`` 型変数から，原稿ごとの対応する修正コメントを保存します．

.. literalinclude:: /py_examples/ex_load_revise_sheet.py
    :language: python
    :lines: 1-10

``revise_items`` は以下の通り簡単に dump できます．

.. literalinclude:: /py_examples/ex_load_revise_sheet.py
    :language: python
    :lines: 12-

出力されるファイルは以下のような形式です．

.. literalinclude:: /py_examples/revise_items.json
    :language: json
    :caption: revise_items.json

.. note::

    ここでの例は単一のレコードのみ保存されていますが，実際のデータは複数のレコードが保存されます．

.. seealso::

    :class:`.ReviseItem`
        原稿修正リクエストの情報を保持するクラス

メールの作成
------------------------------------------

原稿修正リクエストのメールを作成します．
まずは次のような形式でメールテンプレートを作成します．

.. literalinclude:: /py_examples/email_templates/initial_contact.txt
    :language: text
    :caption: initial_contact.txt

本文中に利用可能な変数は以下の通りです．

.. list-table::
    :header-rows: 1

    * - 変数名
      - 説明
    * - ``{name}``
      - 連絡先著者名
    * - ``{title}``
      - 論文タイトル
    * - ``{errors}``
      - 修正メッセージ

以上で準備は整いました．
次の関数でメールの作成を行います．

.. literalinclude:: /py_examples/ex_compose_emails.py
    :language: python

メールの件名（subject）に利用可能な変数は ``{id}`` （Paper ID） のみです．


メールの保存
------------------------------------------

作成したメールを保存します．
送信前に保存することで，メールの内容を確認することができます．

.. literalinclude:: /py_examples/ex_save_emails.py
    :language: python

保存されるメールは MIME 形式のテキストファイルです．

.. literalinclude:: /py_examples/emails/6000.txt
    :language: text
    :caption: 6000.txt


.. _send_mail:

メールの送信
------------------------------------------

SMTP プロトコルを利用して，作成したメールを送信します．
SMTP サーバの設定は環境変数により指定します．
指定可能な環境変数や設定ファイル（``.env``）の書き方は :func:`.handleEmail.send_email` を参照してください．

環境変数を設定した後，次のようにメールを送信します．

.. literalinclude:: /py_examples/ex_send_email.py
    :language: python

.. caution::

    実際にメールを送信する際には，``dry_run`` フラグを ``False`` に設定してください．
    この設定が ``True`` の場合，メールは送信されません．既定値は ``True`` です．

.. note::

    ``dump=True`` とすることで，送信に成功・失敗したメールを保存できます．
    保存先は環境変数 ``DUMP_DIR`` で指定します．
    送信に成功したメールは ``{DUMP_DIR}/email.dump`` に，失敗したメールは ``{DUMP_DIR}/failed_email.dump`` に保存されます．


送信ログの出力
------------------------------------------

本パッケージでは，``logging`` モジュールを利用してメール送信の度にログを出力できます．
メールが正常に送信されているかの確認，あるいは失敗した場合のトラブルシューティングに利用できます．

ログの設定は ``log_config.json`` により行います．以下は簡単な設定例です．

.. literalinclude:: /py_examples/log_config.json
    :language: json
    :caption: log_config.json

設定ファイルは環境変数により指定します．
詳しくは :func:`.handleEmail.send_email` を参照してください．

ログの設定が適切に行われている場合，:ref:`send_mail` 結果として次のような出力が得られます．

.. code-block:: text

    [04/Jul/2024 15:28:34] INFO [email_logger:148] send_mail (dry_run): NOLTA 2023 Publication <ymiino@naruto-u.ac.jp> -> john@example.com: Revision request for paper 6000

