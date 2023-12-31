# 疾病・障害認定審査会のデータまとめ

厚生労働省の[疾病・障害認定審査会](https://www.mhlw.go.jp/stf/shingi/shingi-shippei_127696_00001.html)が行なった審議結果のPDFからデータを抽出する仕組みをまとめたフォルダです。

## 抽出に関して

「疾病・障害認定審査会」のPDFではpythonの`camelot`ライブラリでは抽出が出来ない表が多数あり、そういったPDFについてはMicrosoft Officeの`WORD`や`EXCEL`を用いて一旦csvファイルへとデータを抽出して処理する。

1. PDFファイルを`WORD`で開き、表全体を選択・コピーして`EXCEL`に貼り付ける
1. `EXCEL`のファイル保存画面で`ファイルの種類`に`CSV UTF-8(コンマ区切り) (*.csv)`を選んで保存する
1. `reports-settings.yaml`に抽出のための設定を記述する
1. `reports-settings-all.yaml`にも同じ抽出設定を追記する
1. `create-certified-reports-v1.py`を実行する

```sh
python create-certified-reports-v1
```

### 全てのデータの抽出をやり直したい場合

抽出処理の不具合修正を行なった場合や、データの型を変更した（文字列ではなく文字列の配列に変更する等）場合などに「全てのデータの抽出処理を再度実行したい」という状況があるかと思います。

その場合は、全てのデータ抽出設定を記述した`reports-settings-all.yaml`を引数に指定して以下のようにスクリプトを実行してください。（引数がない場合には、自動的に`reports-settings.yaml`を読み込んで処理するように実装しています。）

```sh
python create-certified-reports-v1.py reports-settings-all.yaml
```

## 抽出結果からサイト用のまとめデータを作る

抽出したデータはJSON形式で`reports-data`フォルダに保存されます。これらのデータを1つに結合しつつ集計も行いサマリ情報を生成する処理は以下で実行できます。

```sh
python sum-certified-reports-v1.py
```

実行結果はひとつ上のフォルダ階層にある`_datasets`フォルダに`certified-reports.json`などのファイル名で保存されます。
