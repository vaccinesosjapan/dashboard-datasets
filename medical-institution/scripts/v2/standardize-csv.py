# %%
import os, re, sys, unicodedata
import pandas as pd
from distutils.util import strtobool

# スクリプトへエクスポートした際に、必要に応じてパスの更新が必要な情報
relative_dir = sys.argv[1]
csv_folder = os.path.join('..', 'intermediate-files', relative_dir)
csv_file_name = sys.argv[2]
has_concurrent_vaccination = bool(strtobool(sys.argv[3]))

csv_file_path = os.path.join(csv_folder, csv_file_name)
original_df = pd.read_csv(csv_file_path)

# %%
# 列の調整。PDFから読み取った内容によっては列の数などが変動して、ここの処理を変える必要があるかも。
df = original_df.copy()

# 2025年からの新データ用
columns = ['no', 'age', 'gender', 'vaccinated_dates', 'vaccine_name', 'lot_no', 'manufacturer', 'concurrent_vaccination_flag', 'concurrent_vaccination', 'pre_existing_disease_names', 'PT_names', 'onset_dates', 'days_to_onset', 'causal_relationship', 'severity', 'gross_result_dates', 'gross_results', 'pt_by_expert', 'causal_relationship_by_expert', 'brighton_classification_by_expert', 'comments_by_expert']
df.columns = columns

# gender列が空っぽの時、「NaNだけの列だからfloatのSeries」という扱いになってしまう。後の処理のため、文字列の列に変換したい。
df['gender'] = df['gender'].astype("string")
df['days_to_onset'] = df['days_to_onset'].astype("string")

# %%
# gender 列がNaNのデータが多数あり。age 列に半角スペース区切りで場合が多く、抽出する。
gender_nan_df = df[df['gender'].isna()]
age_split_df = gender_nan_df['age'].str.split(' ', expand=True)

if age_split_df.shape[1] == 2:
	age_split_df = age_split_df[age_split_df[1].notna()]
	df.loc[age_split_df.index, 'age'] = age_split_df[0]
	df.loc[age_split_df.index, 'gender'] = age_split_df[1]

# %%
# days_to_onset が NaN で、causal_relationshipに「1 評価不能」というような状態でデータが入っているケースへの対処
days_to_onset_nan_df = df[df['days_to_onset'].isna()]
causal_relationship_split_df = days_to_onset_nan_df['causal_relationship'].str.split(' ', expand=True)

if causal_relationship_split_df.shape[1] == 2:
	causal_relationship_split_df = causal_relationship_split_df[causal_relationship_split_df[1].notna()]
	df.loc[causal_relationship_split_df.index, 'days_to_onset'] = causal_relationship_split_df[0]
	df.loc[causal_relationship_split_df.index, 'causal_relationship'] = causal_relationship_split_df[1]

# %%
# 不要な改行の除去
df.loc[:, 'vaccine_name'] = df['vaccine_name'].str.replace('\r\n', '\n').str.replace('\n', '')
df.loc[:, 'pre_existing_disease_names'] = df['pre_existing_disease_names'].str.replace('\r\n', '\n').str.replace('\n', '')
df.loc[:, 'PT_names'] = df['PT_names'].str.replace('\r\n', '\n').str.replace('\n', '')
df.loc[:, 'pt_by_expert'] = df['comments_by_expert'].str.replace('\r\n', '\n').str.replace('\n', '')
df.loc[:, 'comments_by_expert'] = df['comments_by_expert'].str.replace('\r\n', '\n').str.replace('\n', '')

# 大文字と小文字の正規化
df.loc[:, 'vaccine_name'] = df['vaccine_name'].map(lambda x: unicodedata.normalize("NFKC", x))

# %%
# 同時接種したワクチンの扱いが2025年から変わったので対応する

## 同時接種フラグのboolean化
df.loc[:, 'concurrent_vaccination_flag'] = df['concurrent_vaccination_flag'].map(lambda x: x == 'あり')

## concurrent_vaccination は {ワクチン名}（{製造販売業者}、{ロット番号}） というフォーマットで記述されており
## これを {ワクチン名};{製造販売業者};{ロット番号} というセミコロン区切りの文字列に変換したい。
def convert_format_of_concurrent_vaccination(name: str):
    # 不要な改行の除去や、区切りに使う括弧が大文字だったり小文字だったりで安定しないので先に正規化する。
	name = unicodedata.normalize("NFKC", name.replace('\r\n', '\n').replace('\n', '') )

	split_names = name.split('(')
	if len(split_names) < 2:
		print(f'[Warning] concurrent_vaccination が想定のフォーマットではありません: {name}')
		print()
		return name
	
	vaccine_name = split_names[0]

	split_names_2nd = split_names[1].replace(')', '').split('、')
	if len(split_names_2nd) < 2:
		print(f'[Warning] concurrent_vaccination が想定のフォーマットではありません: {name}')
		print()
		return name
	
	manufacturer = split_names_2nd[0]
	lot_no = split_names_2nd[1]

	return f'{vaccine_name};{manufacturer};{lot_no}'


concurrent_vaccine_df = df[df['concurrent_vaccination_flag']]
df.loc[concurrent_vaccine_df.index, 'concurrent_vaccination'] = concurrent_vaccine_df['concurrent_vaccination'].map(lambda x: convert_format_of_concurrent_vaccination(x))

# %%
csv_file_name_without_ext = os.path.splitext(csv_file_name)[0].replace('-pre', '-converted')
csv_file_path = os.path.join(csv_folder, f'{csv_file_name_without_ext}.csv')
with open(csv_file_path, encoding='utf-8', mode='w') as f:
	f.write(df.to_csv(index=False))

# %%
def remove_empty_lines(source_path, target_path):
    fixed_data = ''
    with open(source_path, encoding="utf-8") as f:
        for line in f:
            if line.isspace():
                continue
            if line.startswith('0,1,2,3,4,5'):
                continue
            if line.startswith(','):
                line = re.sub('^,', '', line)
            fixed_data += line

    with open(target_path, "w", encoding="utf-8") as f:
        f.write(fixed_data)


# %%
remove_empty_lines(csv_file_path, csv_file_path)

print(f'{csv_file_path} に整形結果を保存しました。')


