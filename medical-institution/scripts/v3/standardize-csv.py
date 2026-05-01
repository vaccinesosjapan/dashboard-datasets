import os, re, sys, unicodedata, math
import pandas as pd


def apply_concurrent_vaccination_flag(df: pd.DataFrame) -> None:
    '''
    「同時接種」列が空で、一つ前の列に結合されているデータが散見される。
    一つ前の列からデータを抽出して「同時接種」列に適用する。
    引数で受け取ったDataFrameを直接編集する点に注意。
    '''
    df['concurrent_vaccination_flag'] = df['concurrent_vaccination_flag'].fillna('')
    empty_cvf_df = df[df['concurrent_vaccination_flag'] == '']
    vd_split_df = empty_cvf_df['vaccinated_dates'].str.split(' ', expand=True)
    if vd_split_df.shape[1] == 2:
        df.loc[vd_split_df.index, 'vaccinated_dates'] = vd_split_df[0]
        df.loc[vd_split_df.index, 'concurrent_vaccination_flag'] = vd_split_df[1]


def apply_days_to_onset(df: pd.DataFrame) -> None:
	'''
	「接種から症状発生までの日数」の列が空で、一つ後の列と結合されているデータが散見される。
	一つ後の列からデータを抽出して「接種から症状発生までの日数」列に適用する。
	引数で受け取ったDataFrameを直接編集する点に注意。
	'''
	# 数字のセルだけを抽出してint型に変換し、NaNを空文字列に変換してからint型のseriesを適用する。
	dto_number_sr = df[pd.to_numeric(df['days_to_onset'], errors='coerce').notna()]['days_to_onset'].astype(int)
	df['days_to_onset'] = df['days_to_onset'].fillna('').astype(str)
	for index in dto_number_sr.index:
		df.loc[index, 'days_to_onset'] = str(dto_number_sr[index])

	empty_dto_df = df[df['days_to_onset'] == '']
	cr_split_df = empty_dto_df['causal_relationship'].str.split(' ', expand=True)
	if cr_split_df.shape[1] == 2:
		df.loc[cr_split_df.index, 'days_to_onset'] = cr_split_df[0]
		df.loc[cr_split_df.index, 'causal_relationship'] = cr_split_df[1]
	

def remove_newlines(df: pd.DataFrame) -> None:
	'''
	データに不要な改行が含まれている列に対して、改行を削除する処理を行う。
    また、一部データは文字列から文字列配列に変換を行う。
	引数で受け取ったDataFrameを直接編集する点に注意。
	'''
	delete_newline_targets = ['vaccine_name', 'sales_name', 'manufacturer']
	for column_name in delete_newline_targets:
		df.loc[:, column_name] = df[column_name].str.replace('\r\n', '\n').str.replace('\n', '')


def convert_newline_code(df: pd.DataFrame) -> None:
	'''
	CRLFをLFに統一する。別途JSON化する処理時にLFでsplitしてlist化して処理するための準備。
	引数で受け取ったDataFrameを直接編集する点に注意。
	'''
	convert_newline_code_targets = ['pre_existing_disease_names', 'PT_names']
	if 'pt_by_expert' in df.columns:
		convert_newline_code_targets.append('pt_by_expert')
	for column_name in convert_newline_code_targets:
		df.loc[:, column_name] = df[column_name].str.replace('\r\n', '\n')


def convert_date_format(df: pd.DataFrame) -> None:
	'''
	日付のフォーマット「YYYY年MM月DD日」を「YYYY/MM/DD」に変換する。
	「年だけ」や「年と月だけ」といった情報が足りていないデータもあるため、末尾にスラッシュが来る場合はそれを除去する。
	引数で受け取ったDataFrameを直接編集する点に注意。
	'''
	df.loc[:, 'vaccinated_dates'] = df['vaccinated_dates'].str.replace('年', '/').str.replace('月', '/').str.replace('日', '').str.removesuffix('/')
	df.loc[:, 'onset_dates'] = df['onset_dates'].str.replace('年', '/').str.replace('月', '/').str.replace('日', '').str.removesuffix('/')
	df.loc[:, 'gross_result_dates'] = df['gross_result_dates'].str.replace('年', '/').str.replace('月', '/').str.replace('日', '').str.removesuffix('/')


def set_concurrent_vaccination(df: pd.DataFrame) -> None:
	'''
    「同時接種」列をbool型に変換する。
    「同時接種」が『あり』の前後どちらかの行から「同時接種ワクチン」の内容を抽出して設定する。抽出に使った方の行は削除する。
    引数で受け取ったDataFrameを直接編集する点に注意。
    '''
	df.loc[:, 'concurrent_vaccination_flag'] = df['concurrent_vaccination_flag'].map(lambda x: x == 'あり')
	df.insert(5, 'concurrent_vaccination', '')
    
	concurrent_vaccine_df = df[df['concurrent_vaccination_flag']]
	for cv_index in concurrent_vaccine_df.index:
		'''
        後の行がNoなど空の行ならそれを使い、前の行の方がNoなど空の行ならそちらを使う。
        '''
        # cv_index の内容が新型コロナワクチンの内容ではない場合にはneed_replaceをTrueにしてワクチン名や販売名などを入れ替えながら処理する。
		concurrent_vaccine = ''
		need_replace = False
		if not 'コロナ' in df.at[cv_index, 'vaccine_name']:
			need_replace = True
			concurrent_vaccine = f"{str(df.at[cv_index, 'sales_name'])};{str(df.at[cv_index, 'lot_no'])};{str(df.at[cv_index, 'manufacturer'])}"
        
		extraction_index = 0
		if math.isnan(df.at[cv_index+1, 'no']):
			extraction_index = cv_index+1
		elif math.isnan(df.at[cv_index-1, 'no']):
			extraction_index = cv_index-1
		else:
			print(f"同時接種ワクチンの情報が見つかりませんでした, No:{df.at[cv_index, 'no']}")
		
		if need_replace:
			# concurrent_vaccine は作成済みなので内容の入れ替えのみ
			df.loc[cv_index, 'vaccine_name'] = df.at[extraction_index, 'vaccine_name']
			df.loc[cv_index, 'sales_name'] = df.at[extraction_index, 'sales_name']
			df.loc[cv_index, 'lot_no'] = df.at[extraction_index, 'lot_no']
			df.loc[cv_index, 'manufacturer'] = df.at[extraction_index, 'manufacturer']
		else:
			concurrent_vaccine = f"{str(df.at[extraction_index, 'sales_name'])};{str(df.at[extraction_index, 'lot_no'])};{str(df.at[extraction_index, 'manufacturer'])}"
		
		df.loc[cv_index, 'concurrent_vaccination'] = concurrent_vaccine
		df.drop(index=extraction_index, inplace=True)


def normalize_unicodedata(df: pd.DataFrame) -> None:
	'''
	ワクチン名など名称の列にて、大文字・小文字を正規化する。
	引数で受け取ったDataFrameを直接編集する点に注意。
	'''
	target_columns = ['concurrent_vaccination', 'vaccine_name', 'sales_name', 'lot_no', 'manufacturer']
	for column_name in target_columns:
		df.loc[:, column_name] = df[column_name].map(lambda x: unicodedata.normalize("NFKC", str(x)))


def remove_empty_lines(source_path, target_path):
    '''
    保存したCSVファイルに不要な改行が含まれているのを削除する処理。
    '''
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


def main() -> int:
    # スクリプトへエクスポートした際に、必要に応じてパスの更新が必要な情報
	relative_dir = sys.argv[1]
	csv_folder = os.path.join('..', 'intermediate-files', relative_dir)
	csv_file_name = sys.argv[2]
	# sys.argv[3] は、このスクリプトでは使用しない
	id_metadata_kind = sys.argv[4]

	csv_file_path = os.path.join(csv_folder, csv_file_name)
	df = pd.read_csv(csv_file_path, dtype={'ロット番号': str})

	# 第111回からの新データ用の列。
	# 重篤と非重篤とで列が異なるため id_metadata_kind を用いた条件分岐を行う。
	if id_metadata_kind == 'MIS':
		df.columns = ['no', 'age', 'gender', 'vaccinated_dates', 'concurrent_vaccination_flag', 'vaccine_name', 'sales_name', 'lot_no', 'manufacturer', 'pre_existing_disease_names', 'PT_names', 'onset_dates', 'days_to_onset', 'causal_relationship', 'severity', 'gross_result_dates', 'gross_results', 'pt_by_expert', 'causal_relationship_by_expert', 'brighton_classification_by_expert', 'comments_by_expert']
	elif id_metadata_kind == 'MIN':
		# 非重篤の症例一覧では、「専門家」による評価やコメントなどの列が無い。
		df.columns = ['no', 'age', 'gender', 'vaccinated_dates', 'concurrent_vaccination_flag', 'vaccine_name', 'sales_name', 'lot_no', 'manufacturer', 'pre_existing_disease_names', 'PT_names', 'onset_dates', 'days_to_onset', 'causal_relationship', 'severity', 'gross_result_dates', 'gross_results']
	else:
		print(f'不明な id_metadata_kind です: {id_metadata_kind}')
		return 1

	# 全行で列が空っぽ場合、「NaNだけの列だからfloatのSeries」という扱いになってしまう。
	# 後の処理のため、文字列の列に変換する。
	df['gender'] = df['gender'].astype("string")

	apply_concurrent_vaccination_flag(df)
	apply_days_to_onset(df)
	remove_newlines(df)
	convert_newline_code(df)

	## 列が空（NaN）ばかりでfloat64型の列になってることがあるので、空文字でfillしてあらかじめstr型の列にしておく。
	if 'comments_by_expert' in df.columns:
		column_name = 'comments_by_expert'
		df[column_name] =  df[column_name].fillna('')
		df.loc[:, column_name] = df[column_name].str.replace('\r\n', '\n').str.replace('\n', '')

	convert_date_format(df)
	set_concurrent_vaccination(df)
	normalize_unicodedata(df)
	df['no'] = df['no'].astype(int)
	
	csv_file_name_without_ext = os.path.splitext(csv_file_name)[0].replace('-pre', '-converted')
	csv_file_path = os.path.join(csv_folder, f'{csv_file_name_without_ext}.csv')
	with open(csv_file_path, encoding='utf-8', mode='w') as f:
		f.write(df.to_csv(index=False))
    
	remove_empty_lines(csv_file_path, csv_file_path)
	print(f'{csv_file_path} に整形結果を保存しました。')

	return 0


if __name__ == '__main__':
    sys.exit(main())
