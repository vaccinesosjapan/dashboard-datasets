# %%
import os, re, math, sys
import pandas as pd
from distutils.util import strtobool

# スクリプトへエクスポートした際に、必要に応じてパスの更新が必要な情報
csv_folder = os.path.join('..', 'intermediate-files')
csv_file_name = sys.argv[1]
manufacturer = sys.argv[2]
vaccine_name = sys.argv[3]
has_vaccinated_times = bool(strtobool(sys.argv[4]))

csv_file_path = os.path.join(csv_folder, csv_file_name)
original_df = pd.read_csv(csv_file_path)

# %%
# 列の調整。PDFから読み取った内容によっては列の数などが変動して、ここの処理を変える必要があるかも。
df = original_df.copy()

# 「接種回数」の列があるデータの場合、ロット番号の後に追加する
if has_vaccinated_times:
	columns = ['no', 'age', 'gender', 'vaccinated_date', 'onset_date', 'lot_no', 'vaccinated_times', 'pre_existing_disease_names', 'reported_desc', 'PT_names', 'tests_used_for_determination', 'causal_relationship', 'possible_presence_of_other_factors', 'causal_relationship_by_expert_previous', 'comment_previous', 'causal_relationship_by_expert', 'comment', 'document_no', 'case_no']
else:
	columns = ['no', 'age', 'gender', 'vaccinated_date', 'onset_date', 'lot_no', 'pre_existing_disease_names', 'reported_desc', 'PT_names', 'tests_used_for_determination', 'causal_relationship', 'possible_presence_of_other_factors', 'causal_relationship_by_expert_previous', 'comment_previous', 'causal_relationship_by_expert', 'comment', 'document_no', 'case_no']
df.columns = columns

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
# 元の症例一覧には製造販売業者やワクチン名が記載されていないので、引数でもらった情報を使って列を追加する
# PT_names列以外のデータ有無によって処理を分けている箇所があるため、この列挿入は最後に行う必要がある。
df.insert(1, column='manufacturer', value=manufacturer)
df.insert(2, column='vaccine_name', value=vaccine_name)

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


