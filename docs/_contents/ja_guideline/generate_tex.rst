TeX ソースの自動生成
=========================

本パッケージでは，論文の投稿情報を基にした TeX ソースファイル（中間ファイル）の自動生成を行うための関数を提供しています．
関連する機能は :mod:`.json2tex` モジュールに実装されています．

.. note::

    :ref:`ページ番号まで付与 <save_page>` された ``data.json`` をあらかじめ準備しておきましょう．

.. _sso_json:

SS オーガナイザ JSON
---------------------------------------

``data.json`` には，SS オーガナイザの情報が含まれていません．
したがって，別途 ``ss_organizers.json`` を用意する必要があります．
``ss_organizers.json`` は，以下のような形式になります．

.. literalinclude:: /py_examples/ss_organizers.json
    :language: json
    :caption: ss_organizers.json

SS オーガナイザの情報はフォーマットが統一されていないため，``ss_organizers.json`` は手動で作成する必要があります．
``ss_organizers.json`` は，以下のような情報を含む必要があります．

.. list-table::
    :header-rows: 1

    * - キー
      - 値
    * - ``category``
      - SS のカテゴリ（SS の ID に相当）
    * - ``title``
      - SS のタイトル
    * - ``ss_organizers``
      - SS オーガナイザのリスト（:class:`.Person`）

.. hint::

    Publication 担当から SS 担当に定型フォーマットを提供できれば，情報抽出が容易になるかと思います．
    その他，ChatGPT などで整形すると良いかもしれません．

SS list の自動生成
---------------------------------------

SS の情報をまとめたリストを TeX ソースファイルとして出力するためには，以下のスクリプトを実行します．

.. literalinclude:: /py_examples/ex_json2ss_tex.py

出力される TeX ソースファイルは，以下のような形式になります．

.. literalinclude:: /py_examples/ss_list.tex
    :language: latex
    :caption: ss_list.tex

すなわち，TeX システム側で以下の環境，コマンドを定義すれば，``ss_list.tex`` をそのまま include/input できます．

.. code-block:: latex

    \newenvironment{ssSessionTabular}{\begin{tabular}{ll}}{\end{tabular}}
    \newcommand{\ssOrgTabular}[2]{\begin{tabular}{ll}#1&#2\end{tabular}}

もちろん，これらの環境・コマンドは自由にカスタマイズできるので，TeX システム側の仕様・デザインに応じて適宜変更してください．
つまり，Proceedings と Abstract Collection で異なる定義を実装可能です．


.. seealso::
    :func:`.json2ss_tex`
        SS list の自動生成関数

Session Panel の自動生成
---------------------------------------

Session Panel とは，Session の情報をまとめたパネルです．
発行物に掲載するタイムテーブルにおいて，Session の情報を一覧表示するために利用できます．

Session Panel を TeX ソースファイルとして出力するためには，以下のスクリプトを実行します．

.. literalinclude:: /py_examples/ex_json2spanel_texs.py

出力される TeX ソースファイルは，以下のような形式になります．

.. literalinclude:: /py_examples/spanels/A2L.tex
    :language: latex
    :caption: A2L.tex

上記の例では，Chair が 1 名ですが，Chair が複数いる場合は Chairs と表記されます．

``spanels`` ディレクトリに保存された各 TeX ソースファイルは，TeX システム側で以下のコマンドを定義すれば，それぞれ include/input できます．

.. code-block:: latex

    \newcommand{\timeslot}[2]{#1--#2}
    \newcommand{\nosession}{NO SESSION}
    \newcommand{\spanel}[3]{#1\\#2\\#3}

もちろん，これらの環境・コマンドは自由にカスタマイズできるので，TeX システム側の仕様・デザインに応じて適宜変更してください．
つまり，Proceedings と Abstract Collection で異なる定義を実装可能です．


.. seealso::
    :func:`.json2spanel_texs`
        Session Panel の自動生成関数

Papers info の自動生成
---------------------------------------

Papers info とは，論文の情報をセッションごとにまとめた一覧です．
発行物に掲載する抄録集や Technical Program において，セッションや論文の情報を一覧表示するために利用できます．

Papers info を TeX ソースファイルとして出力するためには，以下のスクリプトを実行します．

.. literalinclude:: /py_examples/ex_json2papers_tex.py

出力される TeX ソースファイルは，以下のような形式になります．

.. literalinclude:: /py_examples/papers_information.tex
    :language: latex
    :caption: papers_information.tex

すなわち，TeX システム側で以下の環境，コマンドを定義すれば，``papers_information.tex`` をそのまま include/input できます．

.. code-block:: latex

    \newenvironment{session}[5]{YOUR}{DEFINITION}
    \newcommand{\pEntry}[8]{YOUR DEFINITION}

もちろん，これらの環境・コマンドは自由にカスタマイズできるので，TeX システム側の仕様・デザインに応じて適宜変更してください．
つまり，Proceedings と Abstract Collection で異なる定義を実装可能です．

.. seealso::
    :func:`.json2papers_tex`
        Papers info の自動生成関数