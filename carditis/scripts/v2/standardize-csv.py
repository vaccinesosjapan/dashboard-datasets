# %%
import os, re, json, sys
import pandas as pd

csv_folder = 'intermediate-files'
csv_name = sys.argv[1]
manufacturer = sys.argv[2]

csv_path = os.path.join('..', csv_folder, csv_name)
original_df = pd.read_csv(csv_path, encoding='utf-8')

# %%
# 2025年以降のデータに対応。大幅に列が少なくなり、「経過」列が追加された。
# 年齢と性別が1つの列に結合され、それぞれの情報を中点「・」で繋いだデータになった。分解して別々の列にする。
df = original_df.rename(columns={'0': 'no', '1': 'vaccine_name', '2': 'age_and_gender', '3': 'pre_existing_disease_names', '4': 'keika', '5': 'PT_names', '6': 'gross_results', '7': 'brighton_classification', '8': 'evaluated_result', '9': 'expert_opinion'})

# %%
# 「年齢・性別」データを分割して2つの列にする。
age_and_gender_df = df['age_and_gender'].str.split('・', expand=True)
if len(age_and_gender_df.columns) == 2:
    age_and_gender_df.columns = ['age', 'gender']
    df.insert(1, "age", age_and_gender_df['age'])
    df.insert(2, "gender", age_and_gender_df['gender'])
    df = df.drop('age_and_gender', axis=1)
else:
    print(" - 年齢と性別の分離ができませんでした。データを確認してください。")

# %%
# lot_noの情報がvaccine_name列に含まれているため、これを分離する。「{ワクチン名}\n({ロット番号})」というフォーマットになっている模様。
v_name_and_lot_no_df = df['vaccine_name'].str.replace('\r\n', '\n').str.split('\n', expand=True)
if len(v_name_and_lot_no_df.columns) == 2:
    v_name_and_lot_no_df.columns = ['vaccine_name', 'lot_no']
    df['vaccine_name'] = v_name_and_lot_no_df['vaccine_name']
    df['lot_no'] = v_name_and_lot_no_df['lot_no'].str.replace('(', '').str.replace(')', '')
else:
    print(" - ワクチン名とロット番号の分離ができませんでした。データを確認してください。")

# %%
# 不足している列を追加
df['vaccinated_date'] = ''
df['onset_dates'] = ''
df['days_to_onset'] = ''
df['gross_result_dates'] = ''
df['evaluated_PT'] = ''
df['manufacturer'] = manufacturer
df['vaccinated_times'] = ''
df['remarks'] = ''

# 不要な列を削除
df = df.drop('keika', axis=1)

# 列の並び替え
new_columns = ['no', 'age', 'gender', 'vaccinated_date', 'onset_dates', 'days_to_onset', 'vaccine_name', 'manufacturer', 'vaccinated_times', 'lot_no', 'pre_existing_disease_names', 'PT_names', 'gross_result_dates', 'gross_results', 'evaluated_PT', 'evaluated_result', 'brighton_classification', 'expert_opinion', 'remarks']
df = df.reindex(columns=new_columns)

# %%
with open(csv_path, encoding='utf-8', mode='w') as f:
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
remove_empty_lines(csv_path, csv_path)

print(f'{csv_path} に正規化した結果を保存しました。')
