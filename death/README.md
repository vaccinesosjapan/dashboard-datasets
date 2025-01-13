# Death issues

製造販売業者が発表した新型コロナウイルスワクチンに関する副反応疑い報告のうち、亡くなった方々に関して`専門家`が評価を行った結果の症例一覧を扱うフォルダです。

## 準備

1. `death-table.csv`に使用するPDFの情報などをまとめる。
1. 各PDFの冒頭に掲載されている心筋炎/心膜炎の件数を`expected-issues.csv`にまとめる。
1. 検討部会に関する情報を`metadata.yaml`に記載する。

## 報告一覧の抽出

以下の手順で行う。

1. `reports-settings.yaml`に、特定のPDFの情報を記載する。
1. PDFからCSVファイルにデータ抽出する（`pdf-files`から`intermediate-files`へ）。
    * python _1-extract-pdf-to-csv.py
1. CSVファイルの列ヘッダ部分を手作業で整える
    * 2段組みにしている箇所があり、プログラムでの整形が困難なため。
    * 整形完了したら`*-pre.csv`ファイルに保存する
1. プログラムで表形式データの整形を行う（列とデータの対応がおかしい箇所への対応など）。
    * python _2-standardize-csv.py
    * `intermediate-files`フォルダに、`*-converted.csv`ファイルが作られる
1. プログラムでは対応が難しい表崩れを`手作業`で整形する。
    * `*-converted.csv`ファイルをExcelなどで開き、手作業で表形式がおかしい箇所のデータを整形する。
    * 整形完了したら`*-manually-fixed.csv`ファイルに保存する。
1. 最終的な整形を行ってJSONデータを出力する（`intermediate-files`から`reports-files`へ）。
    * python _3-save-to-json.py

（以降は古い手順、必要なければ削除する予定）

### データの抽出と修正

まず、以下を実行してPDFファイルからデータを抽出します。これにより`extracted-data`フォルダに`JSON`形式でデータが抽出されます。

```sh
python create-death-reports-v1.py
```

一部のデータで、`no`列に統廃合に関する情報などが書かれている場合があります。`no`列が数字に変換可能かをチェックしてデータをより分け、手作業でデータの削除などを実施する必要があります。

上記の`create-death-reports-v1.py`による処理では`select-no.py`も実行することで、`extracted-data`フォルダのすべてのJSONファイルを読み取り、仕分けを行います。`no`列が数字のデータは`reports-data`フォルダに、手作業で修正が必要なデータは`intermediate-files`フォルダに、それぞれJSON形式で保存されます。

`intermediate-files`フォルダ内のJSONを目視で確認しながら、「取り下げ」られた案件や「No.◯◯に統合」と書かれたデータを削除します。統合されて残る方のデータは「No.◯◯と統合」という風に書かれるようなので、誤って消さないよう注意が必要です。

データの統廃合に伴い、年齢や性別、発生日などに取り消し線が書かれたり注釈が書かれることが多々あります。そういったデータも修正したいため、該当する案件をファイルごとにピックアップします。以下を実行します。

```sh
python check-onset-dates.py > _check-result.md
```

保存された`_check-result.md`を見ながら、対象の案件を修正します。

### 集計

上記ができたら、以下を実行することで症例一覧データを作れます。`reports-data`フォルダと`intermediate-files`フォルダの全てのJSONファイルを読み取り、改行などを除去しながら1つのデータにまとめる処理です。

```sh
python sum-death-reports-v1.py
```

別途、PDFの1ページ目の数字をもとに件数を集計したデータが`../_datasets/death-summary.json`に保存されており、これとの件数比較を行うことで手作業などに起因するデータ件数の誤りを確認できます。`../_datasets/`フォルダでpythonを`REPL`モードで起動し、以下を実行すれば症例データによる集計の件数が確認できるので、比較すると良いです。

```sh
import pandas as pd
df = pd.read_json('death-reports.json')
df.groupby(['vaccine_name', 'causal_relationship_by_expert'])['no'].count()
```

## サマリの集計

以下3つのファイルの情報を更新します。

- summary-metadata.yaml
- summary-settings.yaml
- summary-settings-all.yaml

その後、以下を実行します。

```sh
python create-death-summary-v1.py
python sum-death-summary-v1.py
```
