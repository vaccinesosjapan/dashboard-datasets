# Carditis issues

新型コロナウイルスワクチンを接種した後に心筋炎や心膜炎になった方々の報告をまとめるフォルダです。
元となる情報は製造販売業者が発表し、専門家が評価を行ったとする心筋炎/心膜炎の事例を集めた資料です。

## 実行方法

### 報告一覧の抽出

事前に必要なPDFをダウンロードして`pdf-files`フォルダ以下に配置し、`reports-settings.yaml`に記載のファイル名やページ番号などを更新した上で、以下を実行します。

```sh
python create-carditis-reports-v1.py
python sum-carditis-reports-v1.py
```

### 集計情報の抽出

PDFに掲載されている報告一覧を抽出するため、`summary-settings.yaml`に記載のファイル名やページ番号などを更新して以下を実行します。

```sh
python create-carditis-summary-v1.py
```

さらに、抽出した情報を整理してダッシュボード用のデータにするため、`summary-metadata.yaml`に記載の情報ソースに関する設定を更新して以下を実行します。

```sh
python sum-carditis-summary-v1.py
```
