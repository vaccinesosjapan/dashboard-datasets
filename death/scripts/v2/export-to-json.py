# %%
import os, unicodedata, json
import pandas as pd
import ast

# スクリプトをエクスポートした際に調整が必要な各種パス情報
csv_folder = os.path.join('..', 'intermediate-files')
csv_file_name = '001475611-manually-fixed.csv' # sys.argv[1]
expected_issue_count = int('11') # int(sys.argv[2])
json_folder = os.path.join('..', 'reports-data')
json_file_name = '001475611.json' # sys.argv[3]

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
# ワクチン名に全角の数字が含まれていて検索が困難にあるなど弊害があるため、大文字小文字などの違いも対象に正規化
df.loc[:, 'vaccine_name'] = df['vaccine_name'].map(lambda x: unicodedata.normalize("NFKC", x))

# %%
result_issue_count = df.shape[0]
if result_issue_count != expected_issue_count:
	print(f'[Warning] {expected_issue_count} 件のデータのはずが、{result_issue_count} 件のデータになりました。')
	print('手作業時のデータ構造や想定件数の確認が必要と思われます。')
	print()

# %%
df['id'] = df['vaccine_name'].str.cat(df['no'].astype(str), sep='-')

# %%
fixed_df = df.copy()

# PT_namesには、 "['A, 'B', 'C']" というような文字列が入ってしまっているので、astを使って配列として取り出す
fixed_df.loc[:, 'PT_names'] = fixed_df['PT_names'].map(lambda x: ast.literal_eval(x))

# %%
if not 'vaccinated_times' in fixed_df.columns:
	lot_no_column_index = fixed_df.columns.get_loc('lot_no')
	fixed_df.insert(lot_no_column_index + 1, 'vaccinated_times', '')

# %%
# 日付のスラッシュがエスケープされないようにするため、json.dumpsを使って文字列化する
df_dict = fixed_df.to_dict("records")
df_string = json.dumps(df_dict, ensure_ascii=False, indent=2)

json_file_path = os.path.join(json_folder, json_file_name)
with open(json_file_path, encoding='utf-8', mode='w') as f:
	f.write(df_string)

print(f'{json_file_path} にJSON形式で保存しました。')


