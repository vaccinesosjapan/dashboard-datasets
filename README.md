# 副反応ダッシュボード データセット

厚生労働省のサイトにて掲載されている「新型コロナワクチン副反応疑い報告」などの情報をPDFファイルから抽出して、ダッシュボードサイトなどで扱える「データ」として公開するためのリポジトリです。

## データ抽出について

「誰が実施しても同等の抽出結果が得られるようにする」という考えをベースに、Pythonのライブラリ[camelot](https://camelot-py.readthedocs.io/en/master/)を用いてPDFから表を抽出する処理を開発・使用しています。

この`camelot`ライブラリの制約により、`python 3.8`をインストールして使用します。さらに`camelot`が依存している仕組みがあるため、[ここ](https://camelot-py.readthedocs.io/en/master/user/install-deps.html) を見ながらご自身が使用しているOS毎に事前にセットアップが必要です。

`camelot`も含めた、抽出処理で使っているpythonライブラリは以下のコマンドでインストール可能です。

```sh
pip install -r requirements.txt
```

## 用語

厚生労働省が発行している資料で使われている用語と、抽出データの名称の対応関係は基本的に以下のようにしています。

* 番号: no
* 年齢: age
* 性別: gender
* 製造販売業者: manufacturer
* ワクチン名: vaccine_name
* 同時接種: concurrent_vaccination
* 接種日: vaccinated_dates
* 接種回数: vaccinated_times
* 発症日: onset_dates
* 基礎疾患: pre_existing_conditions
* 症状名(PTがある場合): PT_names
* 症状名(PTが無い場合): symptoms
* 判定に用いた検査: tests_used_for_determination
* 因果関係: causal_relationship
* 因果関係（専門家による評価）: causal_relationship_by_expert
* 専門家コメント: comments_by_expert
* 転帰日: outcome_dates
* 転帰内容: outcome
* 認定日: certified_date
* 請求内容: description_of_claim
* 判定結果: judgment_result
* 否認理由: reasons_for_repudiation
* 備考: remarks
