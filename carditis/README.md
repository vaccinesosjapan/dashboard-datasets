# Carditis issues

製造販売業者が発表した新型コロナウイルスワクチンに関する副反応疑い報告のうち、症状が心筋炎や心膜炎に該当する案件に関して`専門家`が評価を行った結果の症例一覧を扱うフォルダです。

## 実行方法

### 準備

過去の期間も含めた更新版のPDFが掲載されることが多いため、「どのPDF（データ）を削除してどれと入れ替えるのか？」を整理する必要がある。

1. `carditis-table.csv`に使用するPDFの情報などをまとめる。
1. 各PDFの冒頭に掲載されている心筋炎/心膜炎の件数を`expected-issues.csv`にまとめる。
1. 検討部会に関する情報を`metadata.yaml`に記載する。

### 報告一覧の抽出

以下の手順で行う。

1. `reports-settings.yaml`に、特定のPDF、特定の症例の情報を記載する。
1. PDFからCSVファイルにデータ抽出する（`pdf-files`から`intermediate-files`へ）。
    * python _1-extract-pdf-to-csv.py
1. プログラムで表形式データの整形を行う（列とデータの対応がおかしい箇所への対応など）。
    * python _2-standardize-csv.py
    * `intermediate-files`フォルダに、`*-converted.csv`ファイルが作られる
1. プログラムでは対応が難しい表崩れを`手作業`で整形する。
    * `*-converted.csv`ファイルをExcelなどで開き、手作業で表形式がおかしい箇所のデータを整形する
    * 整形完了したら`*-manually-fixed.csv`ファイルに保存する
1. 最終的な整形を行ってJSONデータを出力する（`intermediate-files`から`reports-files`へ）。
    * _3-save-to-json.py

うまく処理できたら、`reports-settings.yaml`の内容を`reports-settings-all.yaml`に転記して保管しておく。

### データをまとめる

対象となる全てのPDFで上述の作業が完了したら、以下を実行して症例一覧を1つのデータにまとめる。

```sh
python sum-reports.py
```

### 集計と検証

症例一覧のまとめを更新できたら、以下を実行してメタデータや症例一覧の集計結果などを専用のファイルに保存する。また、以下のスクリプトでは`expected-issues.csv`に記載の件数と抽出したデータの件数を比較検証する機能ももつ。

```sh
python sum-summary.py
```
