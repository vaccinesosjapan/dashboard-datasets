import os, sys, unicodedata
import camelot
import pandas as pd
sys.path.append("../libraries")
from exfuncs import (
	extract_PT_names,
    split_space_and_newline
)

# 引数から情報を取得
pdf_file_name = sys.argv[1]
pages = sys.argv[2]

# 定数
source_dir = 'pdf-files'
output_dir = 'reports-data'

# 抽出処理
pdf_file_path = os.path.join(source_dir, pdf_file_name)
tables = camelot.read_pdf(pdf_file_path, pages=pages, encoding='utf-8')

for index, table in enumerate(tables):
	df = pd.DataFrame(table.df)

	# 整形処理
	df = df.rename(columns={0: 'no'})
	df = df.rename(columns={1: 'age'})
	df = df.rename(columns={2: 'gender'})
	df = df.rename(columns={3: 'vaccinated_date'})
	df = df.rename(columns={4: 'onset_dates'})
	df = df.rename(columns={5: 'days_to_onset'})
	df = df.rename(columns={6: 'vaccine_name'})
	df = df.rename(columns={7: 'manufacturer'})
	#df = df.rename(columns={8: 'lot_no'}) #改行区切りで前の列にくっついてる
	df = df.rename(columns={8: 'pre_existing_disease_names'})
	df = df.rename(columns={9: 'PT_names'})
	df = df.rename(columns={10: 'gross_result_dates'})
	df = df.rename(columns={11: 'gross_results'})
	df = df.rename(columns={12: 'evaluated_PT'})
	df = df.rename(columns={13: 'evaluated_result'})
	df = df.rename(columns={14: 'brighton_classification'})
	df = df.rename(columns={15: 'expert_opinion'})
	df = df.rename(columns={16: 'remarks'})
	df.insert(8, 'lot_no', '')

	# todo: No列を数字に変換する処理もできればここでやりたい
	df[['age','gender']] = df['age'].str.split(' ', expand=True)
	df['age'] = df['age'].map(lambda x: str(x).replace('歳代','').replace('歳',''))
	df['onset_dates'] = df['onset_dates'].str.split('\n')
	df['vaccine_name'] = df['vaccine_name'].map(lambda x: unicodedata.normalize("NFKC", x))
	df[['manufacturer','lot_no']] = df['manufacturer'].str.split('\n', expand=True)
	df['pre_existing_disease_names'] = df['pre_existing_disease_names'].str.split('\n')
	df['PT_names'] = df['PT_names'].map(lambda x: extract_PT_names(x))
	df['gross_result_dates'] = df['gross_result_dates'].str.split('\n')
	df['gross_results'] = df['gross_results'].map(lambda x: split_space_and_newline(x))

	# 保存処理
	json_string = df.to_json(orient='records' ,force_ascii=False, indent=2)
	output_file_name = f'001244797-{index+1}.json'
	output_path = os.path.join(output_dir, output_file_name)
	with open( output_path, "w", encoding='utf-8') as f:
		f.write(json_string)

	print(f'{output_file_name}に {len(df)} [件] 抽出しました')

	# データの妥当性チェック: エラーがあればログ出力
	empty_no = df[df['no'] == '']
	if not empty_no.empty:
		print('No 列が空: 手作業での修正が必要です')
		print(empty_no)
		print()
	empty_days_to_onset = df[df['days_to_onset'] == '']
	if not empty_days_to_onset.empty:
		print('days_to_onset 列が空: 手作業での修正が必要です')
		print(empty_days_to_onset)
		print()
	empty_gross_results = df[df['gross_results'].map(lambda x: len(x) == 0)]
	if not empty_gross_results.empty:
		print('gross_results 列が空: 手作業での修正が必要です')
		print(empty_gross_results)
		print()