# Carditis issues

製造販売業者が発表した新型コロナウイルスワクチンに関する副反応疑い報告のうち、症状が心筋炎や心膜炎に該当する案件に関して`専門家`が評価を行った結果の症例一覧を扱うフォルダです。

## 実行方法

### 報告一覧の抽出

以下の手順で行う。

1. `reports-settings.yaml`に設定情報を記載する
1. PDFからCSVファイルにデータ抽出する（`pdf-files`から`intermediate-files`へ）
    * python _1-extract-pdf-to-csv.py
1. プログラムで表形式データの整形を行う（列とデータの対応がおかしい箇所への対応など）
    * python _2-standardize-csv.py
    * `intermediate-files`フォルダに、`*-converted.csv`ファイルが作られる
1. プログラムでは対応が難しい表崩れを手作業で整形する
    * `*-converted.csv`ファイルをExcelなどで開き、手作業で表形式がおかしい箇所のデータを整形する
    * 整形完了したら`*-manually-fixed.csv`ファイルに保存する
1. 最終的な整形を行ってJSONデータを出力する（`intermediate-files`から`reports-files`へ）
    * _3-save-to-json.py

### 集計情報のデータを作成

1. 各PDFの1ページ目に件数の集計結果が記載されているので、これを`metadata.yaml`に転記する。
1. 以下のコマンドを実行する。集計結果が1つ上の階層の`_datasets`フォルダに`carditis-summary.json`というファイル名で保存される。

```sh
python sum-carditis-summary-v1.py
```

### 抽出した報告一覧の検証

さらに、抽出した症例一覧の情報が意図した件数になっているか確認します。`metadata.yaml`に集計情報が正しく転記されていることを確認して、以下のコマンドを実行します。件数が一致しない場合には、黄色の文字で`[警告]`が表示されます。

```sh
python verify-carditis-reports-v1.py
```

問題なさそうであれば、以下のコマンドを実行して症例一覧を1つにまとめたデータを更新しましょう。これにより、1つ上の階層の`_datasets`フォルダの`carditis-reports.json`が更新されます。

```sh
python sum-carditis-reports-v1.py
```
