import sys, json, os, traceback, math, re
import pandas as pd

csv_file_name = sys.argv[1]
output_file_name = sys.argv[2]
# 第3引数のpagesは、このスクリプトでは不要
manufacturer = sys.argv[4]
vaccine_name = sys.argv[5]
source_dir = 'csv-files'
output_dir = 'extracted-data'

csv_file_path = os.path.join(source_dir, csv_file_name)
if not os.path.exists(csv_file_path):
	print(f'[エラー] csvファイル "{csv_file_path}" が見つかりません')
	sys.exit(1)
df = pd.read_csv(csv_file_path, delimiter=',')

try:
	data = []
	for _, row in df.iterrows():
		# 先にNaNを空白文字列に変換しておく
		for index, cell in enumerate(row):
			if isinstance(cell, float):
				if math.isnan(cell):
					row[index] = ''
				else:
					# 否認理由が区切り文字ピリオドだった場合にもここにくるため、int型への
					# キャストは無しでstring型に変換する
					row[index] = str(cell)

		no = row['No']
		# 後で sum-death-reports スクリプトにて年齢を数字へと加工するようなので、ここではそのままにする
		age = row['年齢(接種時)']
		gender = row['性別']
		vaccinated_date = row['接種日']
		onset_dates = row['発生日(死亡日)'].replace('\r\n', '\n').split('\n')
		lot_no = row['ロット番号']
		pre_existing_conditions = row['基礎疾患等'].replace('\n','')

		PT_names = []
		matched = re.findall(r'(?<=（).*(?=）)', row['死因等(報告者による見解·考察等)-対応するMedDRA PT'])
		if matched:
			for m in matched:
				PT_names.append(m)
		
		tests_used_for_determination = row['報告医が死因等の判断に至った検査'].replace('\n','')
		causal_relationship = row['因果関係(報告医評価)'].replace('\n','')
		causal_relationship_by_expert = row['専門家による評価【最新】-ワクチンと死亡との因果問係評価(評価記号)']
		comments_by_expert = row['専門家による評価【最新】-コメント']

		row = {
			"no": no,
			"manufacturer": manufacturer,
			"vaccine_name": vaccine_name,
			"age": age,
			"gender": gender,
			"vaccinated_dates": vaccinated_date,
			"onset_dates": onset_dates,
			"lot_no": lot_no,
			"vaccinated_times": "", # 旧データ型との互換性のため
			"pre_existing_conditions": pre_existing_conditions,
			"PT_names": PT_names,
			"tests_used_for_determination": tests_used_for_determination,
			"causal_relationship": causal_relationship,
			"causal_relationship_by_expert": causal_relationship_by_expert,
			"comments_by_expert": comments_by_expert
		}

		data.append(row)

	print(f'{len(data)} issues')

	json_string = json.dumps(data, ensure_ascii=False, indent=2)

	if not os.path.exists(output_dir):
		os.mkdir(output_dir)

	output_file_path = os.path.join(output_dir, output_file_name)
	with open( output_file_path, "w", encoding='utf-8') as f:
		f.write(json_string)

except Exception as e:
	print('Exception has occurred :-(')
	print("-"*60)
	print(f'name: {vaccine_name}, len(data): {len(data)}')
	print(f'row: {row}', file=sys.stderr)
	traceback.print_exc(file=sys.stderr)
	print("-"*60)
	print()
	sys.exit(1)