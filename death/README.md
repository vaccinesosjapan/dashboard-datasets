# Death issues

製造販売業者が発表した新型コロナウイルスワクチンに関する副反応疑い報告のうち、亡くなった方々に関して`専門家`が評価を行った結果の症例一覧を扱うフォルダです。

## 準備

1. **death-table.csv** に、使用するPDFの情報をまとめる。
1. 検討部会に関する情報を **metadata.yaml** に記載する。

## 報告一覧の抽出

以下の手順で行う。

1. **reports-settings.yaml** に、PDFから情報を抽出するための情報を記載する。
1. `python _1-extract-pdf-to-csv.py`を実行し、PDFのデータをCSVファイルに保存する。
    * **intermediate-files** フォルダ以下にCSVファイルを作成する。
1. CSVファイルをコピーして、ファイル名末尾に **-pre** をつけて保存する。
1. コピーしたCSVファイルを開き、列ヘッダ部分を手作業で整える。
    * 2段組みにしている箇所があり、プログラムでの整形が困難なため。
1. `python _2-standardize-csv.py`を実行し、データの整形を行う。
    * **-converted** CSVファイルが作られる。
1. CSVファイルをコピーして、ファイル名末尾を **-manually-fixed** にして保存する。
1. コピーしたCSVファイルを開き、手作業で仕上げる。
1. `python _3-save-to-json.py`を実行して、JSONするファイルへと変換する。
    * **reports-files** フォルダに保存される。

**death-table.csv** にメモした全てのPDFに対して、上記の処理ができたら以下を実行する。

1. `python _4-apply-source.py` に **新しく作ったJSONファイルのパス** 渡しながら実行して、 **source** など付加情報を付与する。
1. `python _5-sum-reports.py` を実行して、レポートや集計データを完成させる。
