# %%
import os, re, unicodedata, json, sys
import pandas as pd

csv_folder = 'intermediate-files'
csv_file_name = sys.argv[1] # eg) '001325489-myocarditis-manually-fixed.csv'
expected_issue_count = int(sys.argv[2]) # eg) int('380')
json_file_name = sys.argv[3] # eg) '001325489-myocarditis.json'
source_name = sys.argv[4] # '第104回'
source_url = sys.argv[5] # 'https://www.mhlw.go.jp/content/11120000/001325490.pdf'

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
s1 = df['onset_dates'].str.replace(' ', '')
s2 = s1.str.replace('\r\n', '\n').str.split('\n')

# %%
# 改行を除去して配列にする処理
df.loc[:, 'onset_dates'] = df['onset_dates'].str.replace(' ', '').str.replace('\r\n', '\n').str.split('\n')
df.loc[:, 'pre_existing_disease_names'] = df['pre_existing_disease_names'].str.replace(' ', '').str.replace('\r\n', '\n').str.split('; \n')
df.loc[:, 'gross_result_dates'] = df['gross_result_dates'].str.replace(' ', '').str.replace('\r\n', '\n').str.split('\n')
df.loc[:, 'gross_results'] = df['gross_results'].str.replace(' ', '').str.replace('\r\n', '\n').str.split('\n')
df.loc[:, 'evaluated_PT'] = df['evaluated_PT'].str.replace('\r\n', '\n')
df.loc[:, 'expert_opinion'] = df['expert_opinion'].str.replace('\r\n', '').str.replace('\n', '')
df.loc[:, 'remarks'] = df['remarks'].str.replace('\r\n', '\n').str.replace('\n', '')

# %%
# ワクチン名に全角の数字が含まれていて検索が困難にあるなど弊害があるため、大文字小文字などの違いも対象に正規化
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

json_folder = 'reports-data'
json_file_path = os.path.join(json_folder, json_file_name)
with open(json_file_path, encoding='utf-8', mode='w') as f:
	f.write(df_string)

print(f'{json_file_path} にJSON形式で保存しました。')
