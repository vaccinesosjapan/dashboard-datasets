# %%
import os, re, sys
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

# 「同時接種」の列があるデータの場合、ロット番号の後に追加する
if has_concurrent_vaccination:
	columns = ['no', 'age', 'gender', 'vaccinated_dates', 'onset_dates', 'days_to_onset', 'vaccine_name', 'concurrent_vaccination', 'manufacturer', 'lot_no', 'PT_names', 'causal_relationship', 'severity', 'gross_result_dates', 'gross_results']
else:
	columns = ['no', 'age', 'gender', 'vaccinated_dates', 'onset_dates', 'days_to_onset', 'vaccine_name', 'manufacturer', 'lot_no', 'PT_names', 'causal_relationship', 'severity', 'gross_result_dates', 'gross_results']
df.columns = columns

# %%
# gender 列がNaNのデータが多数あり。age 列に半角スペース区切りで場合が多く、抽出する。
gender_nan_df = df[df['gender'].isna()]
age_split_df = gender_nan_df['age'].str.split(' ', expand=True)

if age_split_df.shape[1] == 2:
	age_split_df = age_split_df[age_split_df[1].notna()]
	df.loc[age_split_df.index, 'age'] = age_split_df[0]
	df.loc[age_split_df.index, 'gender'] = age_split_df[1]

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


