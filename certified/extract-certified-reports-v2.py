import sys, json, os, traceback, math, unicodedata
import pandas as pd
sys.path.append("../libraries")
from excertified import (
	extract_reasons_for_repudiation,
	sum_certified_and_repudiation_count
)

csv_file_name = sys.argv[1]
output_file_name = sys.argv[2]
# 第3引数のpagesは、このスクリプトでは不要
certified_date = sys.argv[4]
reason_type = sys.argv[5]
certified_count = sys.argv[6]
repudiation_count = sys.argv[7]
source_url = sys.argv[8]
source_dir = 'intermediate-files'
output_dir = 'reports-data'

csv_file_path = os.path.join(source_dir, csv_file_name)
if not os.path.exists(csv_file_path):
	print(f'[エラー] csvファイル "{csv_file_path}" が見つかりません')
	sys.exit(1)
df = pd.read_csv(csv_file_path, delimiter=',')

'''
以下のような列ヘッダを持つデータを想定する。

  性別,年齢,ワクチン名,請求内容,疾病名,基礎疾患,判定,否認理由,備考

>>> >>> df.loc[0]
性別              女
年齢            43歳
ワクチン名       新型コロナ
請求内容     医療費・医療手当
疾病名      アナフィラキシー
基礎疾患          NaN
判定             認定
否認理由          NaN
備考            NaN
'''
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

		gender = row['性別']
		age = []
		age_raw = row['年齢']
		if type(age_raw) is str:
			for a in row['年齢'].replace('歳', '').replace('、', ',').split(','):
				age.append(int(a))
		else:
			age.append(int(age_raw))
		vaccine_name = row['ワクチン名']
		description_of_claim = row['請求内容']

		symptoms = []
		if row['疾病名'] != '':
			if len(row['疾病名'].split('、')) > 0:
				for sym_name in row['疾病名'].split('、'):
					symptoms.append(unicodedata.normalize("NFKC", sym_name))
			else:
				symptoms.append(unicodedata.normalize("NFKC", row['疾病名']))

		pre_existing_conditions = []
		if row['基礎疾患'] != '':
			if len(row['基礎疾患'].split('、')) > 0:
				pre_existing_conditions.extend(row['基礎疾患'].split('、'))
			else:
				pre_existing_conditions.append(row['基礎疾患'])

		judgment_result = row['判定']
		reasons_for_repudiation = extract_reasons_for_repudiation(row['否認理由'], reason_type)
		remarks = row['備考']

		# 「保留」はデータに含めない。通しの番号もないため同一の案件か否かを判別する術がなく、最終的に
		# 「保留」から「認定」になったのか「否認」になったのかを追えず意味がないため。
		if judgment_result == '保留':
			continue

		rowData = {
			"certified_date": certified_date,
			"gender": gender,
			"age": age,
			"vaccine_name": vaccine_name,
			"description_of_claim": description_of_claim, 
			"symptoms": symptoms,
			"judgment_result": judgment_result,
			"pre_existing_conditions": pre_existing_conditions,
			"reasons_for_repudiation": reasons_for_repudiation,
			"remarks": remarks,
			"source_url": source_url
		}
		data.append(rowData)

	print(f'{len(data)} [件] 抽出しました')

	c, r, unknown = sum_certified_and_repudiation_count(data)
	if int(certified_count) != c:
		print(f'[警告] 想定する認定件数 {certified_count}, 抽出した認定件数: {c}')

	if int(repudiation_count) != r:
		print(f'[警告] 想定する否認件数 {repudiation_count}, 抽出した否認件数: {r}')

	if unknown != 0:
		print(f'[警告] 判定結果が「認定」「否認」以外の案件が {unknown} [件] 抽出されています')

	if not os.path.exists(output_dir):
		os.mkdir(output_dir)

	json_string = json.dumps(data, ensure_ascii=False, indent=2)
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