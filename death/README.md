# Death issues

製造販売業者が発表した新型コロナウイルスワクチンに関する副反応疑い報告のうち、亡くなった方々に関して`専門家`が評価を行った結果の症例一覧を扱うフォルダです。

## 準備

1. **death-table.csv** に、使用するPDFの情報をまとめる。
1. 検討部会に関する情報を **metadata.yaml** に記載する。

## 報告一覧の抽出

以下の手順を **death-table.csv** に追記した全てのPDFに対して実行する。

1. **reports-settings.yaml** に、PDFから情報を抽出するための情報を記載する。
1. `python _1-extract-pdf-to-csv.py`を実行して、CSVファイルを2つ保存する。
    * **intermediate-files** フォルダ以下の `{pdfファイル名}.csv`と`{pdfファイル名}-pre.csv`
1. `{pdfファイル名}-pre.csv`を開き、手作業で整える。
1. `python _2-standardize-csv.py`を実行し、データの整形を行う。
    * **intermediate-files** フォルダ以下の `{pdfファイル名}-converted.csv`と`{pdfファイル名}-manually-fixed.csv`の2つ
1. `{pdfファイル名}-manually-fixed.csv`を開き、手作業で仕上げる。
1. `python _3-save-to-json.py`を実行して、JSONファイルへと変換する。
    * **reports-files** フォルダ以下の`{pdfファイル名}.json`
1. `python _4-apply-source.py {pdfファイル名}.json` を実行して、JSONに **source** 情報を付与する。

上記の繰り返し処理ができたら、サマリ生成のために以下を実行する。

1. `python _5-sum-reports.py` を実行して、レポートや集計データを完成させる。

## 懸案事項

* 報告医評価（`causal_relationship`）に半角や全角のハイフンが記載されている症例が増えつつあるが、これは何を意味するのだろうか？評価していないということ？評価したが不明ということ？分からない。
