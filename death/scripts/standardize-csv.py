# %%
import os, re, sys
import pandas as pd
from distutils.util import strtobool

# スクリプトへエクスポートした際に、必要に応じてパスの更新が必要な情報
csv_folder = os.path.join('..', 'intermediate-files')
csv_file_name = sys.argv[1]
manufacturer = sys.argv[2]
vaccine_name = sys.argv[3]
has_vaccinated_times = bool(strtobool(sys.argv[4]))

csv_file_path = os.path.join(csv_folder, csv_file_name)
original_df = pd.read_csv(csv_file_path, encoding='utf-8')

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
	for index, row in need_manually_fix_df.iterrows():
		number = row['no']
		print(f'Index {index}, No {number} のデータは、後続の行にデータが分散していると思われます。手作業で修正してください。')

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
		pt_name = [ number_df.loc[previous_index, 'PT_names'] ]
		number_df.at[previous_index, 'PT_names'] = pt_name

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
	pt_name = [ number_df.loc[previous_index, 'PT_names'] ]
	number_df.at[previous_index, 'PT_names'] = pt_name

# %%
# 元の症例一覧には製造販売業者やワクチン名が記載されていないので、引数でもらった情報を使って列を追加する
# PT_names列以外のデータ有無によって処理を分けている箇所があるため、この列挿入は最後に行う必要がある。
df.insert(1, column='manufacturer', value=manufacturer)
df.insert(2, column='vaccine_name', value=vaccine_name)

# %%
fixed_df = df.drop(merged_index)
fixed_df['no'] = fixed_df['no'].fillna(-1)
fixed_df.loc[number_df.index, 'no'] = number_df['no']
fixed_df['no'] = fixed_df['no'].astype(int)
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


