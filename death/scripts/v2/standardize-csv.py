# %%
import os, re, math, sys
import pandas as pd
from distutils.util import strtobool

# スクリプトへエクスポートした際に、必要に応じてパスの更新が必要な情報
csv_folder = os.path.join('..','intermediate-files')
csv_file_name = sys.argv[1]
manufacturer = sys.argv[2]
vaccine_name = sys.argv[3]

csv_file_path = os.path.join(csv_folder, csv_file_name)
original_df = pd.read_csv(csv_file_path)

# %%
# 列の調整。PDFから読み取った内容によっては列の数などが変動して、ここの処理を変える必要があるかも。
df = original_df.copy()

# 第106回のデータ対応
columns = ['no', 'vaccine_name', 'lot_no', 'age', 'gender','pre_existing_conditions', 'vaccinated_dates', 'onset_dates', 'PT_names', 'causal_relationship', 'causal_relationship_by_expert', 'comments_by_expert', 'reported_date', 'goudou_reported_date', 'goudou_evaluated_date']
df.columns = columns

# 後半の「死亡症例として報告を受けた日付」、「合同部会報告日」、「合同部会評価日」は使用しないため削除する
df = df.drop(['reported_date', 'goudou_reported_date', 'goudou_evaluated_date'], axis=1)

# 元の症例一覧に含まれない「製造販売業者」列などを追加する。
df.insert(1, column='manufacturer', value=manufacturer)
df.insert(2, column='vaccinated_times', value='')
df.insert(3, column='tests_used_for_determination', value='')

# 最終的にデータ化する時のために列の並べ替えをやっておく。
df = df.reindex(columns=['no', 'manufacturer', 'vaccine_name', 'age', 'gender', 'vaccinated_dates', 'onset_dates', 'lot_no', 'vaccinated_times', 'pre_existing_conditions', 'PT_names', 'tests_used_for_determination', 'causal_relationship', 'causal_relationship_by_expert', 'comments_by_expert'])

# %%
# No列に値が入った行だけを抽出する。
# このインデックスからインデックスの間に、PT_namesのデータが行に分かれて入っているので、マージする。
number_df = df[df['no'].notna()]

# またnumber_dfのcausal_relationship_by_expert列がNaNになっているデータは、表の形が崩れていて他の
# データも後の行に分散してしまっているデータと思われるので、手作業で修正するようログを残す。
need_manually_fix_df = number_df[number_df['causal_relationship_by_expert'].isna()]
if not need_manually_fix_df.empty:
	print('以下のデータは、後続の行にデータが分散していると思われます。手作業で修正してください。')
	for index, row in need_manually_fix_df.iterrows():
		number = f'{row["no"]}'.replace('\r\n', '\n').replace('\n', '')
		print(f'- Index: {index}, No: {number}')
	print()

# %%
# マージした行のインデックスを保持して後ほどdrop処理に使う
merged_index = []

previous_index = 0
for index, _ in number_df.iterrows():
	if index == 0: continue

	if previous_index in need_manually_fix_df.index:
		print(f'Index {previous_index} は手作業の対象のためマージ処理をスキップします。')
	elif index - 1 > previous_index:
		# マージが必要な行が previous_index+1 から index-1 までのインデックスに存在する
		pt_names = []
		sub_index = previous_index+1
		while sub_index < index:
			pt_names.append(df.loc[sub_index, 'reported_desc'])
			merged_index.append(sub_index)
			sub_index += 1
		number_df.at[previous_index, 'PT_names'] = pt_names
	else:
		# マージ不要なケース、PT_namesの内容を配列に変更する
		pt_name = number_df.loc[previous_index, 'PT_names']
		if type(pt_name) == float:
			number_value = f'{number_df.loc[previous_index, "no"]}'.replace('\r\n', '\n').replace('\n', '')
			if math.isnan(pt_name):
				print(f'Index {previous_index}, No {number_value} は、PT_namesがNanです。手作業による修正が必要です。')
			else:
				print(f'Index {previous_index}, No {number_value} は、PT_namesがfloatです。手作業による修正が必要です。')
		else:
			pt_names = pt_name.replace('\r\n', '\n').split('\n')
			number_df.at[previous_index, 'PT_names'] = pt_names

	previous_index = index

# %%
# 最後の行も処理する。
# previous_indexにはnumber_dfの最後のインデックスが格納された状態でここに来るので、

# dfの最後のインデックス。
# previous_indexよりもlast_indexの方が大きい数字の場合、マージ処理の要否を確認しながら処理が必要。
last_index = df.shape[0] - 1

if previous_index in need_manually_fix_df.index:
	print(f'Index {previous_index} は手作業の対象のためマージ処理をスキップします。')
elif last_index > previous_index:
	# マージが必要な行が previous_index+1 から last_index までのインデックスに存在する
	pt_names = []
	sub_index = previous_index+1
	while sub_index <= last_index:
		pt_names.append(df.loc[sub_index, 'reported_desc'])
		merged_index.append(sub_index)
		sub_index += 1
	number_df.at[previous_index, 'PT_names'] = pt_names
else:
	# マージ不要なケース、PT_namesの内容を配列に変更する
	pt_name = number_df.loc[previous_index, 'PT_names']
	if type(pt_name) == float:
		number_value = f'{number_df.loc[previous_index, "no"]}'.replace('\r\n', '\n').replace('\n', '')
		if math.isnan(pt_name):
			print(f'Index {previous_index}, No {number_value} は、PT_namesがNanです。手作業による修正が必要です。')
		else:
			print(f'Index {previous_index}, No {number_value} は、PT_namesがfloatです。手作業による修正が必要です。')
	else:
		pt_names = pt_name.replace('\r\n', '\n').split('\n')
		number_df.at[previous_index, 'PT_names'] = pt_names

# %%
fixed_df = df.drop(merged_index)

# %%
float_no_series = pd.to_numeric(fixed_df['no'], errors='coerce')
no_nan_series = float_no_series[float_no_series.isna()]
if no_nan_series.count() > 0:
	print('以下のデータは、No列の値を数値に変換できません。手作業で修正してください。')
	for index in no_nan_series.index:
		no_value = f'{fixed_df.loc[index, "no"]}'.replace('\r\n', '\n').replace('\n', '')
		print(f'Index: {index}, No: "{no_value}"')

int_no_series = float_no_series[float_no_series.notna()].astype(int)
fixed_df.loc[int_no_series.index, 'no'] = int_no_series

# %%
fixed_df.loc[number_df.index, 'PT_names'] = number_df['PT_names']

# %%
# ageとgender列が、うまく分離できていないケースを処理する。

## age 列が NaN になってるケース。半角スペース区切りで gender 列にデータが入っている場合があるので抽出を試行
age_nan_df = fixed_df[fixed_df['age'].isna()]
extracted_from_gender_df = age_nan_df['gender'].str.split(' ', expand=True)
## gender 列が NaN になってるケース。半角スペース区切りで age 列にデータが入っている場合があるので抽出を試行
gender_nan_df = fixed_df[fixed_df['gender'].isna()]
gender_nan_df['age'] = gender_nan_df['age'].astype(str)
extracted_from_age_df = gender_nan_df['age'].str.split(' ', expand=True)

## 先に dtype を変更しておかないと警告がでたりするので、先に処理する
fixed_df['age'] = fixed_df['age'].astype(str)
fixed_df['gender'] = fixed_df['gender'].astype(str)

if len(extracted_from_gender_df.columns) == 2:
	extracted_from_gender_df.columns = ['age', 'gender']
	fixed_df.loc[extracted_from_gender_df.index, 'age'] = extracted_from_gender_df['age']
	fixed_df.loc[extracted_from_gender_df.index, 'gender'] = extracted_from_gender_df['gender']

if len(extracted_from_age_df.columns) == 2:
	extracted_from_age_df.columns = ['age', 'gender']
	fixed_df.loc[extracted_from_age_df.index, 'age'] = extracted_from_age_df['age']
	fixed_df.loc[extracted_from_age_df.index, 'gender'] = extracted_from_age_df['gender']

# %%
if fixed_df['vaccinated_dates'].dtype != type(str):
	fixed_df['vaccinated_dates'] = fixed_df['vaccinated_dates'].map('{:.0f}'.format).fillna('')
	fixed_df['vaccinated_dates'] = fixed_df['vaccinated_dates'].astype(str)

# %%
# vaccinated_dates が 20241211 のように8桁の数字で表現されているデータを見つけて 2024/12/11 というフォーマットの文字列にしたい
target_vd_df = fixed_df[fixed_df['vaccinated_dates'].str.len() == 8]
not_target_vd_df = fixed_df[fixed_df['vaccinated_dates'].str.len() != 8]

if not target_vd_df.empty:
	fixed_df.loc[target_vd_df.index, 'vaccinated_dates'] = target_vd_df['vaccinated_dates'].map(lambda x: pd.to_datetime(x).strftime("%Y/%m/%d"))

if not not_target_vd_df.empty:
	print("以下のデータについては、vaccinated_dates 列の日付データに関して手動で調整が必要です。")
	for index, row in not_target_vd_df.iterrows():
		print(f' - No. {row.no} (Index: {index})')
	print()

# %%
if fixed_df['onset_dates'].dtype != type(str):
	fixed_df['onset_dates'] = fixed_df['onset_dates'].map('{:.0f}'.format).fillna('')
	fixed_df['onset_dates'] = fixed_df['onset_dates'].astype(str)

# %%
# onset_dates が 20241211 のように8桁の数字で表現されているデータを見つけて 2024/12/11 というフォーマットの文字列にしたい
target_od_df = fixed_df[fixed_df['onset_dates'].str.len() == 8]
not_target_od_df = fixed_df[fixed_df['onset_dates'].str.len() != 8]

if not target_od_df.empty:
	fixed_df.loc[target_od_df.index, 'onset_dates'] = target_od_df['onset_dates'].map(lambda x: pd.to_datetime(x).strftime("%Y/%m/%d"))

if not not_target_od_df.empty:
	print("以下のデータについては、onset_dates 列の日付データに関して手動で調整が必要です。")
	for index, row in not_target_od_df.iterrows():
		print(f' - No. {row.no} (Index: {index})')
	print()

# %%
# 性別が（医療機関からの報告とは逆に）2025年のデータから「女/男」ではなく「女性/男性」と表記されているため、
# 過去データに合わせて「女/男」に統一する
fixed_df['gender'] = fixed_df['gender'].str.replace('女性', '女').str.replace('男性', '男')

# %%
csv_file_name_without_ext = os.path.splitext(csv_file_name)[0].replace('-pre', '-converted')
csv_file_path = os.path.join(csv_folder, f'{csv_file_name_without_ext}.csv')
with open(csv_file_path, encoding='utf-8', mode='w') as f:
	f.write(fixed_df.to_csv(index=False))

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

# %%
print(f'{csv_file_path} に抽出結果を保存しました。')
