# %%
import os, re, json, sys
import pandas as pd

csv_folder = 'intermediate-files'
csv_file_name = sys.argv[1]

csv_file_path = os.path.join('..', csv_folder, csv_file_name)
original_df = pd.read_csv(csv_file_path, encoding='utf-8')

# %%
# 列の調整。PDFから読み取った内容によっては列の数などが変動して、ここの処理を変える必要があるかも。
df = original_df.rename(columns={'0': 'no', '1': 'age', '2': 'gender', '3': 'vaccinated_date', '4': 'onset_dates', '5': 'days_to_onset', '6': 'vaccine_name', '7': 'pre_existing_disease_names', '8': 'PT_names', '9': 'gross_result_dates', '10': 'gross_results', '11': 'evaluated_PT', '12': 'evaluated_result', '13': 'brighton_classification', '14': 'expert_opinion', '15': 'remarks'})
df.insert(7, column='manufacturer', value='')
df.insert(8, column='lot_no', value='')
df.insert(9, column='vaccinated_times', value='')
df = df.drop(0, axis=0)

# %%
###
# パターン1:
# 列インデックス「days_to_onset」の値がNaNになっているパターンを処理する関数。
# このパターンの主な特徴は以下。詳しくはData Wranglerでp1_dfを確認。
#   - 次の「vaccine_name」列に、「days_to_onset」の数字が半角スペース区切りで入っていることが多い
#   - 半角スペースで区切った後の情報は、vaccine_nameなど以降の列データが改行区切りで入っていることが多い
###
def standardize_pattern_one(df):
	p1_df = df[df['days_to_onset'].isna()]
	p1_can_not_fix_df = pd.DataFrame()

	# 半角スペース区切りの場合もあれば、改行区切りの場合もあり。データによってまちまちのようなので全て改行「\n」に変換してから区切る。
	p1_days_df = p1_df['vaccine_name'].str.replace('\r\n', '\n').str.replace(' ', '\n').str.split('\n', expand=True)

	if p1_days_df.shape[1] == 5:
		days_columns = ['days_to_onset', 'vaccine_name', 'manufacturer', 'lot_no', 'vaccinated_times']
		p1_days_df.columns = days_columns
		p1_df.loc[p1_days_df.index, days_columns] = p1_days_df
	elif p1_days_df.shape[1] == 3:
		# こういうパターンもある
		days_columns = ['days_to_onset', 'vaccine_name', 'manufacturer']
		p1_days_df.columns = days_columns
		p1_df.loc[p1_days_df.index, days_columns] = p1_days_df
	else:
		# 意図しているデータではないので、ログ出力を行うようにする。
		p1_can_not_fix_df = pd.concat([p1_can_not_fix_df, p1_df.loc[p1_days_df.index,:]])

	return p1_df, p1_can_not_fix_df

###
# パターン2:
# 列インデックス「gender」の値がNaNになっているパターンを処理する関数。
# このパターンの主な特徴は以下。詳しくはData Wranglerでp2_dfを確認。
#   - 「age」列に、半角スペース区切りでgender文字列も入っていることが多い
###
def standardize_pattern_two(df):
	p2_df = df[df['gender'].isna()]

	p2_age_df = p2_df['age'].str.split(' ', expand=True)
	if(p2_age_df.shape[1] == 2):
		p2_age_df.columns = ['age', 'gender']
	else:
		p2_age_df = pd.DataFrame()
		print('パターン2: age,gender 情報をうまく分割できなかったため手作業での修正が必要です。')
		for index, row in p2_df.iterrows():
			print(f' - No. {row.no} (Index: {index})')
		print()

	return p2_age_df

###
# パターン3:
# 列がズレているために、列インデックス「evaluated_PT」にγなどが含まれているパターン。
# このパターンの主な特徴は以下。詳しくはData Wranglerでp3_dfを確認。
#   - 年齢と性別が、半角スペース区切りでNo列に集約されている
#   - 他の行と比較すると、列インデックス「vaccinated_date」以降の列が左に1つズレている
###
def standardize_pattern_three(df):
	p3_df = df[df['evaluated_PT'].str.contains('α|β|γ', na=False)]

	p3_shift_df = p3_df.shift(periods=1, axis='columns')
	p3_shift_df.loc[p3_shift_df.index, 'no'] = p3_shift_df['age']
	p3_shift_df['age'] = ''
	p3_shift_df.loc[p3_shift_df.index, 'pre_existing_disease_names'] = p3_shift_df['manufacturer']
	p3_shift_df['manufacturer'] = ''

	p3_shift_no_df = p3_shift_df['no'].str.split(' ', expand=True)
	if p3_shift_no_df.shape[1] == 3:
		no_columns = ['no', 'age', 'gender']
		p3_shift_no_df.columns = no_columns
		p3_shift_df.loc[p3_shift_no_df.index, no_columns] = p3_shift_no_df
	else:
		print('パターン3: no列のデータをうまく分割できなかったため手作業での修正が必要です。')
		for index, row in p3_shift_df.iterrows():
			print(f' - No. {row.no} (Index: {index})')
		print()

	return p3_shift_df

###
# パターン4:
# days_to_onsetに数字とvaccine_name文字列が両方入っており、分離が必要なパターン。
# このパターンの主な特徴は以下。詳しくはData Wranglerでp4_dfを確認。
#   - days_to_onsetに日数とワクチン名が入っている
#   - vaccine_nameの列にmanufacturerなどが改行区切りで入っている
#   - 複数行からなるデータの場合、もっとたくさんデータが入っている場合があるが、自動処理が難しいのでそれらはNoを出力すべく返す
###
def standardize_pattern_four(df):
	p4_df = df[df['days_to_onset'].str.contains('[0-9] .*', na=False)]

	p4_fix_df = pd.DataFrame()
	p4_days_df = p4_df['days_to_onset'].str.split('\r\n', expand=True)
	if p4_days_df.shape[1] == 1:
		p4_days_df.columns = ['days']
		# 修正不可のデータは無し、という判定
		p4_can_not_fix_df = p4_df.loc[[]]
		p4_fix_df = p4_df
	elif p4_days_df.shape[1] == 2:
		p4_days_df.columns = ['days', 'second_days']

		# 複数行がまとまったデータは、days_to_onsetにさらに他の数字や文字列が続くため、second_daysがNaNではなくなる
		# それらのややこしいデータは手作業で修正するため、修正不可データとして返す
		p4_can_not_fix_sub_df = p4_days_df[p4_days_df['second_days'].isna().map(lambda x: not x)]
		p4_can_not_fix_df = p4_df.loc[p4_can_not_fix_sub_df.index]

		# 修正可能なデータたちの、列入れ替えを行う
		p4_fix_df = p4_df[p4_days_df['second_days'].isna()]
	else:
		p4_can_not_fix_df = p4_df

	# ここでは修正できるデータが無い
	if p4_fix_df.empty:
		return pd.DataFrame(), p4_can_not_fix_df

	p4_fix_df.loc[p4_fix_df.index, 'manufacturer'] = p4_df['vaccine_name']
	p4_fix_df.loc[p4_fix_df.index, 'vaccine_name'] = ''

	## days_to_onset 列のデータが日数の数字とワクチン名の組み合わせになっているデータなので、これを分離して別々の列に適用する
	p4_day_vac_df = p4_fix_df['days_to_onset'].str.split(' ', expand=True)
	if p4_day_vac_df.shape[1] == 2:
		day_vac_columns = ['days_to_onset', 'vaccine_name']
		p4_day_vac_df.columns = day_vac_columns
		p4_fix_df.loc[p4_day_vac_df.index, day_vac_columns] = p4_day_vac_df
	else:
		p4_can_not_fix_df = pd.concat([p4_can_not_fix_df, p4_df.loc[p4_day_vac_df.index]])

	## manufacturer にlot_noなど複数のデータが含まれているデータなので、これらを分離して別々の列に適用する
	p4_man_lot_df = p4_fix_df['manufacturer'].str.replace('\r\n', '\n').str.split('\n', expand=True)
	if p4_man_lot_df.shape[1] < 3:
		# うまく分離できていないデータのため、想定と異なるデータと思われる。
		# 手作業で修正してもらえるようにログ出力を行う。
		p4_can_not_fix_df = pd.concat([p4_can_not_fix_df, p4_df.loc[p4_man_lot_df.index]])
	elif p4_man_lot_df.shape[1] == 3:
		man_lot_columns = ['manufacturer', 'lot_no', 'vaccinated_times']
		p4_man_lot_df.columns = man_lot_columns
		p4_fix_df.loc[p4_man_lot_df.index, man_lot_columns] = p4_man_lot_df
	else:
		# たくさんのデータが含まれている場合にここにくる。
		# 列インデックス0〜2がNaNではなく、それ以降の列がNaNのデータだけは上述の処理と同様に処理可能。
		# それ以外は手作業でないと難しいのでログ出力する。
		p4_man_lot_can_fix = p4_man_lot_df[0].notna() & p4_man_lot_df[1].notna() & p4_man_lot_df[2].notna() & p4_man_lot_df[3].isna()
		p4_man_lot_can_fix_df = p4_man_lot_df[p4_man_lot_can_fix].loc[:, [0,1,2]]
		man_lot_columns = ['manufacturer', 'lot_no', 'vaccinated_times']
		p4_man_lot_can_fix_df.columns = man_lot_columns
		p4_fix_df.loc[p4_man_lot_can_fix_df.index, man_lot_columns] = p4_man_lot_can_fix_df

		p4_man_lot_can_not_fix = ~p4_man_lot_can_fix
		p4_man_lot_can_not_fix_df = p4_df[p4_man_lot_can_not_fix]
		p4_can_not_fix_df = pd.concat([p4_can_not_fix_df, p4_man_lot_can_not_fix_df])

	p4_df.loc[p4_fix_df.index, :] = p4_fix_df

	return p4_df, p4_can_not_fix_df

###
# パターン5:
# days_to_onset が「不明」になっていて、ワクチン名以降の列を改行区切りで分離する必要があるデータを処理する。
###
def standardize_pattern_five(df):
	p5_df = df[df['days_to_onset'] == '不明']
	man_columns = ['vaccine_name', 'manufacturer', 'lot_no', 'vaccinated_times']
	p5_can_not_fix_df = pd.DataFrame()

	p5_man_df = p5_df['vaccine_name'].str.replace('\r\n', '\n').str.split('\n', expand=True)
	if p5_man_df.shape[1] < 4:
		p5_can_not_fix_df = pd.concat([p5_can_not_fix_df, p5_df.loc[p5_man_df.index, :]])
	elif p5_man_df.shape[1] == 4:
		p5_man_df.columns = man_columns
		p5_df.loc[p5_man_df.index, man_columns] = p5_man_df
	else:
		p5_man_can_fix = p5_man_df[0].notna() & p5_man_df[1].notna() & p5_man_df[2].notna() & p5_man_df[3].notna() & p5_man_df[4].isna()
		p5_man_can_fix_df = p5_man_df[p5_man_can_fix].loc[:, [0,1,2,3]]

		p5_man_can_fix_df.columns = man_columns
		p5_df.loc[p5_man_can_fix_df.index, man_columns] = p5_man_can_fix_df

		p5_man_can_not_fix = ~p5_man_can_fix
		p5_man_can_not_fix_df = p5_df[p5_man_can_not_fix]
		p5_can_not_fix_df = pd.concat([p5_can_not_fix_df, p5_df.loc[p5_man_can_not_fix_df.index, :]])

	return p5_df, man_columns, p5_can_not_fix_df

###
# パターン6:
# gender 列に年齢や接種日の情報がまとまっている場合の処理。
###
def standardize_pattern_six(df):
	p6_df = df['gender'].str.split(' ', expand=True)
	if(p6_df.shape[1] != 3):
		return pd.DataFrame(), pd.Series()
	
	p6_columns = ['age', 'gender', 'vaccinated_date']
	p6_df.columns = p6_columns
	p6_df = p6_df[p6_df.notna().all(axis=1)]
	
	return p6_df, p6_columns

# %%
# パターン3の処理（列がズレており、大きく修正が必要なパターン。この修正の後、もっと普通の修正が必要な状態になるため先に処理する。）
p3_df = standardize_pattern_three(df)
df.loc[p3_df.index, :] = p3_df

# %%
# パターン4の処理
p4_df, p4_can_not_fix_df = standardize_pattern_four(df)
df.loc[p4_df.index, :] = p4_df
if not p4_can_not_fix_df.empty:
	print('以下のNo.の項目は、days_to_onset に複数項目が含まれているため手作業での修正が必要です。')
	for index, row in p4_can_not_fix_df.iterrows():
		print(f' - No. {row.no} (Index: {index})')
	print()

# %%
# パターン1の処理
p1_df, p1_can_not_fix_df = standardize_pattern_one(df)
df.loc[p1_df.index, :] = p1_df
if not p1_can_not_fix_df.empty:
	print('以下のNo.の項目は、days_to_onset をうまく分割できなかったため手作業での修正が必要です。')
	for index, row in p1_can_not_fix_df.iterrows():
		print(f' - No. {row.no} (Index: {index})')
	print()

# %%
# パターン2の処理
p2_df = standardize_pattern_two(df)
df.loc[p2_df.index, ['age', 'gender']] = p2_df

# %%
# パターン5の処理
p5_df, p5_columns, p5_can_not_fix_df = standardize_pattern_five(df)
if not p5_df.empty:
	df.loc[p5_df.index, p5_columns] = p5_df
if not p5_can_not_fix_df.empty:
	print('以下のNo.の項目は、days_to_onset が「不明」のデータを整形できなかったため手作業での修正が必要です。')
	for index, row in p5_can_not_fix_df.iterrows():
		print(f' - No. {row.no} (Index: {index})')
	print()

# %%
# パターン6の処理
p6_df, p6_columns = standardize_pattern_six(df)
df.loc[p6_df.index, p6_columns] = p6_df

# %%
# 処理が不可能なデータをログ出力する

## 複数行からなるデータの2行目以降の場合などが多いデータだが、自動処理にするよりも
## 目視で確認しながら手作業で修正したほうが良いデータ。
no_empty_df = df[df['no'].isna()]
if not no_empty_df.empty:
	print('No.列が空の項目があります。No.列の値に「Invalid」という文字列を適用しますので、手作業での修正をお願いします。')
	print()
	df.loc[no_empty_df.index, 'no'] = 'Invalid'

## 種々の処理を行ったが age がN/Aのデータ。目視の手作業で修正が必要なデータ。
age_na_df = df[df['age'].isna()]
if not age_na_df.empty:
	print('age 列がNAの項目があります。以下のNo.のデータについて、手作業での修正をお願いします。')
	for index, row in age_na_df.iterrows():
		print(f' - No. {row.no} (Index: {index})')
	print()

## 種々の処理を行ったが vaccinated_date がN/Aのデータ。目視の手作業で修正が必要なデータ。
vaccinated_date_na_df = df[df['vaccinated_date'].isna()]
if not vaccinated_date_na_df.empty:
	print('vaccinated_date 列がNAの項目があります。以下のNo.のデータについて、手作業での修正をお願いします。')
	for index, row in vaccinated_date_na_df.iterrows():
		print(f' - No. {row.no} (Index: {index})')
	print()

## 種々の処理を行ったが manufacturer が空文字列のデータ。これも目視しながら手作業で修正した方が良いデータ。
manufacturer_empty_df = df[df['manufacturer'] == '']
if not manufacturer_empty_df.empty:
	print('Manufacturer 列が空の項目があります。以下のNo.のデータについて、手作業での修正をお願いします。')
	for _, row in manufacturer_empty_df.iterrows():
		print(f' - No. {row.no}')
	print()

# %%
csv_file_name_without_ext = os.path.splitext(csv_file_name)[0]
csv_file_path = os.path.join('..', csv_folder, f'{csv_file_name_without_ext}-converted.csv')
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
