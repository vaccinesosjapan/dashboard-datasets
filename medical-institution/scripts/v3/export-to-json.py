import os, json, sys
import pandas as pd


def convert_age_to_int(df: pd.DataFrame) -> None:
	'''
	age 列から「歳」などの文字を除去し、数字に変換できるセルのみint型の数字にする。
	引数で受け取ったDataFrameを直接編集する点に注意。
	'''
	age_is_number_df = df[df['age'].map(lambda x: str(x).replace('歳', '').isdecimal())]
	age_is_number_df.loc[:, 'age'] = age_is_number_df['age'].map(lambda x: int(str(x).replace('歳', '')))
	df.loc[age_is_number_df.index, 'age'] = age_is_number_df


def add_source_columns(df: pd.DataFrame, source_name: str, source_url: str) -> None:
	'''
	情報元のページURLなどをsource列として追加する。
	引数で受け取ったDataFrameを直接編集する点に注意。
	'''
	source_array = [{ "name": source_name, "url": source_url }] * df.shape[0]
	df['source'] = source_array


def add_id_column(df: pd.DataFrame, source_url: str, id_metadata_number: str, id_metadata_kind: str) -> None:
	'''
	検討部会などの情報を用いて、症例にユニークなIDを付与する。
	引数で受け取ったDataFrameを直接編集する点に注意。
	'''
	# ID情報を一覧に追加する
	file_name = source_url.split("/").pop().replace(".pdf", "")
	# 「{検討部会の番号}-{PDFファイル名}-{重篤/非重篤の識別子}-{そのPDF内でのNo}」をIDとする。
	# 第105回以降のデータを処理する本ファイルでは、「PDFファイル名」も使わないとユニークにはならない。
	# 一方で、第104回までは「注：「No」は、全新型コロナワクチンに係る副反応疑い報告（医療機関からの報告）の通番」
	# という扱いであったため、末尾に「No」を使うことでユニークな文字列になっていた。
	df.insert(0, 'id', df['no'].map(lambda x: f'{id_metadata_number}-{file_name}-{id_metadata_kind}-{x}'))


def convert_to_list(df: pd.DataFrame) -> None:
	'''
	基礎疾患や接種日など、一部のデータは改行コードでsplitしてlist化する。
	引数で受け取ったDataFrameを直接編集する点に注意。
	'''
	split_targets = ['vaccinated_dates', 'PT_names', 'pre_existing_disease_names', 'onset_dates', 'days_to_onset', 'gross_result_dates', 'gross_results']
	for column_name in split_targets:
		df.loc[:, column_name] = df[column_name].str.replace('\r\n', '\n').str.split('\n')


def main():
	# スクリプトをエクスポートした際に調整が必要な各種パス情報
	relative_dir = sys.argv[1]
	csv_folder = os.path.join('..', 'intermediate-files', relative_dir)
	csv_file_name = sys.argv[2]
	expected_issue_count = int(sys.argv[3])
	json_folder = os.path.join('..', 'reports-data')
	json_file_name = sys.argv[4]
	source_name = sys.argv[5]
	source_url = sys.argv[6]
	id_metadata_number = sys.argv[7]
	id_metadata_kind = sys.argv[8]

	csv_file_path = os.path.join(csv_folder, csv_file_name)
	df = pd.read_csv(csv_file_path, delimiter=',', 
				  dtype={'lot_no': str, 'days_to_onset': str})

	# このあとの各種処理をしやすくするため、NaNは空文字列に置換しておく。
	df = df.fillna('')
	df = df.sort_values('no')

	convert_age_to_int(df)
	add_source_columns(df, source_name, source_url)
	add_id_column(df, source_url, id_metadata_number, id_metadata_kind)
	convert_to_list(df)

	# pt_by_expert は訳あって、『複数項目を「、」でつないだ文字列』に変換しないといけない。
	if 'pt_by_expert' in df.columns:
		df.loc[:, 'pt_by_expert'] = df['pt_by_expert'].str.replace('\r\n', '\n').str.replace('\n', '、')

	result_issue_count = df.shape[0]
	if result_issue_count != expected_issue_count:
		print(f'[Warning] {expected_issue_count} 件のデータのはずが、{result_issue_count} 件のデータになりました。')
		print('手作業時のデータ構造や想定件数の確認が必要と思われます。')
		print()
	
	# 日付のスラッシュがエスケープされないようにするため、json.dumpsを使って文字列化する
	df_dict = df.to_dict("records")
	df_string = json.dumps(df_dict, ensure_ascii=False, indent=2)

	json_file_path = os.path.join(json_folder, json_file_name)
	with open(json_file_path, encoding='utf-8', mode='w', newline='\n') as f:
		f.write(df_string)

	print(f'{json_file_path} にJSON形式で保存しました。')


if __name__ == '__main__':
	main()
