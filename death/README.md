# Death issues

製造販売業者が発表した新型コロナウイルスワクチンに関する副反応疑い報告のうち、亡くなった方々に関して`専門家`が評価を行った結果の症例一覧を扱うフォルダです。

## 準備

1. `death-table.csv`に、使用するPDFの情報をまとめる。
1. 検討部会に関する情報を`metadata.yaml`に記載する。

## 報告一覧の抽出

以下の手順で行う。

1. `reports-settings.yaml`に、PDFから情報を抽出するための情報を記載する。
1. PDFからCSVファイルにデータ抽出する（`pdf-files`から`intermediate-files`へ）。
    * python _1-extract-pdf-to-csv.py
1. CSVファイルの列ヘッダ部分を手作業で整える
    * 2段組みにしている箇所があり、プログラムでの整形が困難なため。
    * 整形完了したら`*-pre.csv`ファイルに保存する
1. プログラムで表形式データの整形を行う（列とデータの対応がおかしい箇所への対応など）。
    * python _2-standardize-csv.py
    * `intermediate-files`フォルダに、`*-converted.csv`ファイルが作られる
1. `*-converted.csv`を`*-manually2.csv`へとコピーし、ログの内容に従って`手作業`で修正する。
    * `*-manually2.csv`ファイルをExcelなどで開き、手作業で表形式がおかしい箇所のデータを整形する。
1. `scripts/convert-no.ipynb`で`*-manually2.csv`を指定して実行する
    * 修正されたデータが`*-manually3.csv`ファイルに保存される。
1. `*-manually3.csv`を`*-manually-fixed.csv`へとコピーし、再度手作業で仕上げる
1. 最終的な整形を行ってJSONデータを出力する（`intermediate-files`から`reports-files`へ）。
    * python _3-save-to-json.py

`death-table.csv`にメモした全てのPDFで処理ができたら、

1. `try-apply-source.ipynb`を実行して、新形式の`id`や`source`データを個々のJSONデータに付与。
1. `try-sum-reports.ipynb`を実行して、レポートや集計データを完成させる。
