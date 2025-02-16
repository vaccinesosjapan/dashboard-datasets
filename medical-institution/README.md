# 予防接種法に基づく医療機関からの副反応疑い報告

* [第53回厚生科学審議会予防接種・ワクチン分科会副反応検討部会](https://www.mhlw.go.jp/stf/newpage_17208.html)から報告が始まった。
* 第74回まで累計で報告されており、第75回以降からは「前回との差分」の期間に対する報告に変更されている。
* 第88回から、「同時接種」という列が追加された。

## 手作業時の注意

* `lot_no`は文字列にすること。
  * 「"lot_no":9999」というように数字として記載してしまうと、フロントエンド側が内部でエラー起こす。
  * これについてフロントエンド側でタイプチェックしてエラーが起きないようにするという処置も考えられたが、多くの項目に対してタイプチェックを実施することによるパフォーマンス低下が懸念されるためデータを修正するようにした。
  * 問題箇所の有無をチェックするには、VSCodeなどの検索ツールで正規表現をOnにして「"lot_no": [^" ]」や「"lot_no":[^" ]」を検索すればよい。

## 手順

1. 新しいPDFを`pdf-files`フォルダにダウンロードする。
1. ダウンロードしたPDFのファイル名やリンクURLなどを`reports-settings.yaml`に記入する。
1. 同じ内容を`reports-settings-all.yaml`に記載の配列末尾にも追記する。
1. 以下のコマンドを実行して、PDFからCSV形式でデータ抽出する。
    * `python _1-extract-pdf-to-csv.py`
    * 抽出結果は `./intermediate-files./{relative_dir}/{file_id}.csv` に保存される。
1. CSVを開き、ヘッダ情報を手作業で追加して`{file_id}-pre.csv`に保存する。
1. 以下のコマンドを実行して、CSVのデータを整形する。
    * `python _2-standardize-csv.py`
    * 抽出結果は `./intermediate-files./{relative_dir}/{file_id}-converted.csv` に保存される。
1. CSVを開き、列がおかしくなっている箇所などが無いか目視で確認し、必要に応じて手作業で修正する。
    * `VSCode`の`EditCSV`拡張や`Excel`で開いて確認するとスムーズ。
    * 修正結果は `./intermediate-files./{relative_dir}/{file_id}-manually-fixed.csv` に保存する。
1. 以下のコマンドを実行して、データの最終的な整形をしつつCSVをJSONに変換して保存する。
    * `python _3-save-to-json.py`

WIP

1. `summary-metadata.yaml` を更新する。
1. `sum-medical-institution-reports-v1.py` を実行する。
