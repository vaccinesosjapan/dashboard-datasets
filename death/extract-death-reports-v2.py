import json, traceback, os, sys
import camelot
sys.path.append("../libraries")
from exdeath import (
	extract_lot_no_etc
)

'''
亡くなった方々の症例一覧から情報を抽出するスクリプト。

- 「接種回数」無し
- 「専門家による評価」が2つ
'''
pdf_file_name = sys.argv[1]
output_file_name = sys.argv[2]
pages = sys.argv[3]
manufacturer = sys.argv[4]
vaccine_name = sys.argv[5]
source_dir = 'pdf-files'
output_dir = 'extracted-data'

pdf_file_path = os.path.join(source_dir, pdf_file_name)
tables = camelot.read_pdf(pdf_file_path, pages=pages, encoding='utf-8')

try:
	data = []
	for table in tables:
		if table.shape[0] < 2:
			continue

		rowCount = table.df.shape[0]
		for rowIndex in range(3, rowCount):
			row = table.df.loc[rowIndex,:]

			gender, vaccinated_dates, onset_dates, lot_no = extract_lot_no_etc(row[2], row[3], row[4], row[5])

			rowData = {
				"no": row[0],
				"manufacturer": manufacturer,
				"vaccine_name": vaccine_name,
				"age": row[1],
				"gender": gender,
				"vaccinated_dates": vaccinated_dates,
				"onset_dates": onset_dates,
				"lot_no": lot_no,
				"vaccinated_times": "",
				"pre_existing_conditions": row[6].replace('\n',''),
				"PT_names": row[8].split('\n'),
				"tests_used_for_determination": row[9].replace('\n',''),
				"causal_relationship": row[10].replace('\n',''),
				"causal_relationship_by_expert": row[14],
				"comments_by_expert": row[15]
			}

			if rowData['no'] == '':
				data[len(data)-1]['pre_existing_conditions'] = data[len(data)-1]['pre_existing_conditions'] + '\n' + rowData['pre_existing_conditions']
				data[len(data)-1]['PT_names'].extend(rowData['PT_names'])
			else:
				data.append(rowData)


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
	print(f'name: {vaccine_name}, rowIndex: {rowIndex}, len(data): {len(data)}')
	print(f'row: {row}', file=sys.stderr)
	traceback.print_exc(file=sys.stderr)
	print("-"*60)
	print()
	sys.exit(1)