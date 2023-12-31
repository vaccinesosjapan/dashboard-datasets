# 副反応ダッシュボード データセット

厚生労働省のサイトにて掲載されている「新型コロナワクチン副反応疑い報告」などの情報をPDFファイルから抽出して、ダッシュボードサイトなどで扱える「データ」として公開するためのリポジトリです。

## データ抽出について

「誰が実施しても同等の抽出結果が得られるようにする」という考えをベースに、Pythonのライブラリ[camelot](https://camelot-py.readthedocs.io/en/master/)を用いてPDFから表を抽出する処理を開発・使用しています。

この`camelot`ライブラリの制約により、`python 3.8`をインストールして使用します。さらに`camelot`が依存している仕組みがあるため、[ここ](https://camelot-py.readthedocs.io/en/master/user/install-deps.html) を見ながらご自身が使用しているOS毎に事前にセットアップが必要です。

`camelot`も含めた、抽出処理で使っているpythonライブラリは以下のコマンドでインストール可能です。

```sh
pip install -r requirements.txt
```

## 新型コロナワクチン以前のワクチンに関して

厚生労働省の[こちらのページ](https://www.mhlw.go.jp/topics/bcg/other/6.html)で統計が発表されているので、必要ならこれを使うと良さそう。
