# Carditis issues

製造販売業者が発表した新型コロナウイルスワクチンに関する副反応疑い報告のうち、症状が心筋炎や心膜炎に該当する案件に関して`専門家`が評価を行った結果の症例一覧を扱うフォルダである。

## 準備

### メタデータの記載

過去の期間も含めた更新版のPDFが掲載されることが多く、データ抽出に用いたPDFの情報をまとめる。

1. `carditis-table.csv`にPDFの情報をまとめる。
1. PDF冒頭に記載の心筋炎/心膜炎の件数を`expected-issues.csv`にまとめる。
1. 検討部会の情報を`metadata.yaml`に記載する。

### PDFの分割

心筋炎(`myocarditis`)と心膜炎(`pericarditis`)とで。症例一覧のPDFを分割しておく。
例えば、情報ソースのPDFが`001325489.pdf`で、心筋炎の症例一覧が`P30からP45`に掲載されている場合、以下のようにする。

```sh
pdftk 001325489.pdf cat 30-45 output 001325489-myocarditis.pdf
```

この分割したPDFファイルのファイル名`001325489-myocarditis`を、後述の`reports-settings.yaml`で指定する。

※ `pdftk`コマンドを別途インストールしておく。

## 症例一覧の抽出

`reports-settings.yaml`に、抽出対象PDFのデータを書き込み以下のようにスクリプトを実行する。
途中で指示が出たら、VSCodeの`Edit CSV`などを用いて手作業でCSVファイルを修正しつつ作業を続行する。
最終的に`reports-data`ディレクトリにJSONデータが保存される。

```sh
python _convert-pdf-to-json.py
```

## データをまとめる

対象となる全てのPDFで上述の作業が完了したら、以下を実行して症例一覧を1つのデータにまとめる。

```sh
python sum-reports.py
```

## 集計と検証

症例一覧のまとめを更新できたら、以下を実行してメタデータや症例一覧の集計結果などを専用のファイルに保存する。また、以下のスクリプトでは`expected-issues.csv`に記載の件数と抽出したデータの件数を比較検証する機能ももつ。

```sh
python sum-summary.py
```
