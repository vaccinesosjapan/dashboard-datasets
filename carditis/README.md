# Carditis issues

製造販売業者が発表した新型コロナウイルスワクチンに関する副反応疑い報告のうち、症状が心筋炎や心膜炎に該当する案件に関して`専門家`が評価を行った結果の症例一覧を扱うフォルダです。

## 実行方法

### 報告一覧の抽出

1. 事前に心筋炎や心膜炎の報告が記載されたPDFファイルをダウンロードして`pdf-files`フォルダ以下に配置する。
1. `reports-settings.yaml`にデータ抽出のために必要な情報を記載する。
    - プログラムなどによる抽出が困難なPDFファイルの場合があり、その場合はWindowsの`Snipping tool`などのOCR機能（画像内の文字を認識してテキストデータ化する機能）を駆使した手作業が必要になる。
    - 手作業でCSVファイルに抽出した場合は、`intermediate-files`フォルダに置く。
1. 以下のコマンドを実行する。結果は`reports-data`フォルダにJSON形式で保存される。

```sh
python create-carditis-reports-v1.py
```

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
