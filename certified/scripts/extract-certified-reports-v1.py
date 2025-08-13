import sys, json, os, traceback
import camelot
sys.path.append("../libraries")
from excertified import (
	extract_description_of_claim_etc,
	extract_judgment_result_etc_v1,
	extract_reasons_for_repudiation,
	sum_certified_and_repudiation_count
)

pdf_file_name = sys.argv[1]
output_file_name = sys.argv[2]
pages = sys.argv[3]
certified_date = sys.argv[4]
reason_type = sys.argv[5]
certified_count = sys.argv[6]
repudiation_count = sys.argv[7]
source_url = sys.argv[8]
source_dir = 'pdf-files'
output_dir = 'reports-data'

pdf_file_path = os.path.join(source_dir, pdf_file_name)
tables = camelot.read_pdf(pdf_file_path, pages=pages, encoding='utf-8')

'''
以下のように抽出されるテーブル用

>>> tables[0].df.loc[1,:]
0    女\n52歳 新型コロナ\n医療費・医療手当
1              アナフィラキシー\n認定
'''
try:
	data = []
	for table in tables:
		if table.df.loc[0,0].find('審議件数') > -1 or table.df.loc[0,0].find('否認理由') > -1 or table.df.loc[0,1].find('対象疾病名') > -1:
			continue # 処理対象の表ではないのでスキップ

		rowCount = table.df.shape[0]
		for rowIndex in range(0, rowCount):
			if table.df.loc[rowIndex,0].find('性別') > -1:
				continue # ヘッダ行は抽出処理しないのでスキップ

			row = table.df.loc[rowIndex,:]
			gender, age, vaccine_name, description_of_claim = extract_description_of_claim_etc(row[0])
			symptoms, judgment_result, rfr, remarks = extract_judgment_result_etc_v1(row[1])

			# 「保留」はデータに含めない。通しの番号もないため同一の案件か否かを判別する術がなく、最終的に
			# 「保留」から「認定」になったのか「否認」になったのかを追えず意味がないため。
			if judgment_result == '保留':
				continue

			reasons_for_repudiation = extract_reasons_for_repudiation(rfr, reason_type)

			rowData = {
				"certified_date": certified_date,
				"gender": gender,
				"age": age,
				"vaccine_name": vaccine_name,
				"description_of_claim": description_of_claim, 
				"symptoms": symptoms,
				"judgment_result": judgment_result,
				"pre_existing_conditions": [], # 基礎疾患が記述される前のデータ用なので空リストで
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
	print(f'name: {vaccine_name}, rowIndex: {rowIndex}, len(data): {len(data)}')
	print(f'row: {row}', file=sys.stderr)
	traceback.print_exc(file=sys.stderr)
	print("-"*60)
	print()
	sys.exit(1)