# 亡くなった方々に関する症例の集計

## データの抽出と修正

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

## 集計

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
