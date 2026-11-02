# Death issues

製造販売業者が発表した新型コロナウイルスワクチンに関する副反応疑い報告のうち、亡くなった方々に関して`専門家`が評価を行った結果の症例一覧を扱うフォルダです。

## 準備

1. **death-table.csv** に、使用するPDFの情報をまとめる。
1. 検討部会に関する情報を **metadata.yaml** に記載する。

## 報告一覧の抽出

### PDFごとに行う処理

以下の手順を **death-table.csv** に追記した全てのPDFに対して実行する。

1. **reports-settings.yaml** に、PDFから情報を抽出するための情報を記載する
1. `uv run _1-extract-pdf-to-csv.py` を実行する
    * 結果、 **intermediate-files** フォルダ以下に `{pdfファイル名}.csv` と `{pdfファイル名}-pre.csv` が作成される
1. `{pdfファイル名}-pre.csv` を開き、手作業で整える
    * 「年齢（単位）」の列は削除して対応する（`v2`スクリプトの仕様）
1. `uv run _2-standardize-csv.py` を実行し、データの整形を行う
    * 結果、 **intermediate-files** フォルダ以下に `{pdfファイル名}-converted.csv` と `{pdfファイル名}-manually-fixed.csv` が作成される
1. `{pdfファイル名}-manually-fixed.csv` を開き、手作業で仕上げる
1. `uv run _3-save-to-json.py` を実行する
    * 結果、 **reports-files** フォルダ以下に `{pdfファイル名}.json` が作成される
1. `uv run _4-apply-source.py {pdfファイル名}.json` を実行する
    * 結果、 上述の手順で作成したJSONファイルに **source** 情報が付与される

### まとめの処理

上記の繰り返し処理ができたら、サマリ生成のために以下を実行する。

1. `uv run _5-sum-reports.py` を実行して、レポートや集計データを完成させる。

## 懸案事項

* 報告医評価（`causal_relationship`）に半角や全角のハイフンが記載されている症例が増えつつあるが、これは何を意味するのだろうか？評価していないということ？評価したが不明ということ？分からない。
