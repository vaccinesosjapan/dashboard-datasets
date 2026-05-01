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

医療機関からの報告（重篤、非重篤の両方）に対して、以下の手順を実行する。

1. 新しいPDFを「pdf-files」フォルダにダウンロードする。
1. ダウンロードしたPDFのファイル名やリンクURLなどを「**reports-settings.yaml**」に記入する。
1. 同じ内容を「**reports-settings-all.yaml**」の末尾にも追記する。
1. フォルダ 「./intermediate-files./{relative_dir}」 を作る。
1. コマンド`python _1-extract-pdf-to-csv.py`を実行して、PDFからCSV形式でデータを抽出する。
    * 抽出結果は 「**{file_id}.csv**」と「**{file_id}-pre.csv**」 に保存される。
1. 「**{file_id}-pre.csv**」を手作業で編集する。
1. コマンド`python _2-standardize-csv.py`を実行して、CSVのデータを整形する。
    * 抽出結果は「**{file_id}-converted.csv**」と「**{file_id}-manually-fixed.csv**」に保存される。
1. 「**{file_id}-manually-fixed.csv**」を手作業で編集する。
    * 「VSCode」の「EditCSV」拡張や「Excel」で開いて確認するとスムーズ。
1. コマンド`python _3-save-to-json.py`を実行して、JSONファイルへとデータを保存する。

一通りのPDFに対して上記手順を実行できたら、最後にサマリ情報を更新する。

1. 「**summary-metadata.yaml**」 を更新する。
1. `python _4-sum-reports.py` を実行する。
1. `python _5-generate-id-with-sorting.py` を実行する。

さらに、件数の集計情報を更新する。

1. `mi-counts`ディレクトリに移動する。
1. `ordinal_number.yaml`を更新する。
1. `uv run main.py`を実行する。
