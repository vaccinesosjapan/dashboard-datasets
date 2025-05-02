# %%
import os, re, unicodedata, json, sys
import pandas as pd

# スクリプトをエクスポートした際に調整が必要な各種パス情報
relative_dir = sys.argv[1]
csv_folder = os.path.join('..', 'intermediate-files', relative_dir)
csv_file_name = sys.argv[2]
expected_issue_count = int(sys.argv[3])
json_folder = os.path.join('..', 'reports-data')
json_file_name = sys.argv[4]
source_name = sys.argv[5]
source_url = sys.argv[6]

csv_file_path = os.path.join(csv_folder, csv_file_name)
df = pd.read_csv(csv_file_path, delimiter=',')

# %%
# このあとの各種処理をしやすくするため、NaNは空文字列に置換しておく。
df = df.fillna('')

# %%
# age 列に関して、「歳」を除去すれば年齢を数字に変換できるセルだけ処理する
age_is_number_df = df[df['age'].map(lambda x: x.replace('歳', '').isdecimal())]
age_is_number_df.loc[:, 'age'] = age_is_number_df['age'].map(lambda x: int(x.replace('歳', '')))
df.loc[age_is_number_df.index, 'age'] = age_is_number_df

# %%
# 全角のかっこ（）に囲まれたPT名だけを抽出し、各行にPT名の配列を格納したSeriesを取得する
regex = re.compile('(?<=（).+?(?=\）)')
split_PT_names_series = df['PT_names'].map(lambda x: regex.findall(x.replace('\r\n', '')))
df.loc[split_PT_names_series.index, 'PT_names'] = split_PT_names_series

# %%
if df['days_to_onset'].dtype != type(str):
	print('days_to_onset 列が数字のみのため文字列型に変更します')
	df['days_to_onset'] = df['days_to_onset'].astype(str)

# %%
# 改行を除去して配列にする処理と、Windowsの改行（\r\n）を（\n）に変換する処理
df.loc[:, 'vaccinated_dates'] = df['vaccinated_dates'].str.replace(' ', '').str.replace('\r\n', '\n').str.split('\n')
df.loc[:, 'onset_dates'] = df['onset_dates'].str.replace(' ', '').str.replace('\r\n', '\n').str.split('\n')
df.loc[:, 'days_to_onset'] = df['days_to_onset'].str.replace('\r\n', '\n').str.split('\n')
df.loc[:, 'manufacturer'] = df['manufacturer'].str.replace('\r\n', '\n').str.replace('\n', '')
df.loc[:, 'gross_result_dates'] = df['gross_result_dates'].str.replace(' ', '').str.replace('\r\n', '\n').str.split('\n')
df.loc[:, 'gross_results'] = df['gross_results'].str.replace(' ', '').str.replace('\r\n', '\n').str.split('\n')

# %%
# ワクチン名に全角の数字が含まれていて検索が困難にあるなど弊害があるため、大文字小文字などの違いも対象に正規化
df.loc[:, 'vaccine_name'] = df['vaccine_name'].str.replace('\r\n', '\n').str.replace('\n', '')
df.loc[:, 'vaccine_name'] = df['vaccine_name'].map(lambda x: unicodedata.normalize("NFKC", x))

# %%
result_issue_count = df.shape[0]
if result_issue_count != expected_issue_count:
	print(f'[Warning] {expected_issue_count} 件のデータのはずが、{result_issue_count} 件のデータになりました。')
	print('手作業時のデータ構造や想定件数の確認が必要と思われます。')
	print()

# %%
# ソースの情報を一覧に追加する
source_array = [{ "name": source_name, "url": source_url }] * df.shape[0]
df['source'] = source_array

# %%
# 日付のスラッシュがエスケープされないようにするため、json.dumpsを使って文字列化する
df_dict = df.to_dict("records")
df_string = json.dumps(df_dict, ensure_ascii=False, indent=2)

json_file_path = os.path.join(json_folder, json_file_name)
with open(json_file_path, encoding='utf-8', mode='w') as f:
	f.write(df_string)

print(f'{json_file_path} にJSON形式で保存しました。')


