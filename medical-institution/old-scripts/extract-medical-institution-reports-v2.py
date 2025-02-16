import sys, json, re, os, traceback
import camelot

pdf_file_name = sys.argv[1]
output_file_name = sys.argv[2]
pages = sys.argv[3]
expected_count = sys.argv[4]
source_name = sys.argv[5]
source_url = sys.argv[6]
source_dir = 'pdf-files'
output_dir = 'reports-data'

pdf_file_path = os.path.join(source_dir, pdf_file_name)
tables = camelot.read_pdf(pdf_file_path, pages=pages, encoding='utf-8')

# 第88回以降の「同時接種」列が追加されたPDF用
try:
	data = []
	for table in tables:
		rowCount, _ = table.df.shape
		for rowIndex in range(rowCount):
			row = table.df.loc[rowIndex]

			no = row[0]
			if no == 'No':
				# ヘッダー行は処理しない
				continue

			'''
			以下のようなパターンに対応するため、row[0]が空でrow[1]が空でなく
			かつrow[1]のスペース区切り2つ目に「歳代」があるなら・・という
			処理を書く
			0
			1     57 30歳代 男性
			2
			'''
			if row[0] == '' and len(row[1].split(' ')) > 2 and row[1].split(' ')[1].find('歳代') > 0:
				no = row[1].split(' ')[0]
				age = row[1].split(' ')[1]
				gender = row[1].split(' ')[2]
			else:
				if no.isdecimal():
					no = int(no)
				
				age_and_gender = row[1].split(' ')
				age = ''
				gender = ''
				if len(age_and_gender) > 0:
					age = age_and_gender[0].replace('歳', '')
					if age.isdecimal():
						age = int(age)

				if row[2] != '':
					gender = row[2]
				elif len(age_and_gender) > 1:
					gender = age_and_gender[1]

			days_to_onset = []
			vaccine_name = ''
			if row[5] != '' and row[5].isdecimal():
				days_to_onset.append(int(row[5]))
				vaccine_name = row[6]
			else:
				days_and_vaccine = row[6].split(' ')
				if len(days_and_vaccine) > 1:
					vaccine_name = days_and_vaccine[1]
					dto = days_and_vaccine[0]
					if dto.isdecimal():
						days_to_onset.append(int(dto))
					else:
						days_to_onset.append(dto)
				elif len(days_and_vaccine) > 0:
					row6item = days_and_vaccine[0]
					if row6item.isdecimal():
						days_to_onset.append(int(row6item))
					elif row6item == '不明':
						days_to_onset.append(row6item)
					else:
						vaccine_name = row6item
			
			PT_names = []
			matched = re.findall(r'(?<=（).*(?=）)', row[10])
			if matched:
				for m in matched:
					PT_names.append(m)

			row = {
				"no": no,
				"age": age,
				"gender": gender,
				"vaccinated_dates": row[3].split('\n'),
				"onset_dates": row[4].replace('\r\n', '\n').split('\n'),
				"days_to_onset": days_to_onset,
				"vaccine_name": vaccine_name,
				"concurrent_vaccination": row[7],
				"manufacturer": row[8],
				"lot_no": row[9],
				"PT_names": PT_names,
				"causal_relationship": row[11],
				"severity": row[12],
				"gross_result_dates": row[13].replace('\r\n', '\n').split('\n'),
				"gross_results": row[14].replace('\r\n', '\n').split('\n'),
				"source": {
					"name": source_name,
					"url": source_url
				}
			}

			if row['no'] == '':
				previous_row = data[len(data)-1]
				separator = '\n'

				# sourceは結合不要
				keysOfStr = ['age', 'gender', 'vaccine_name', 'manufacturer', 'lot_no',
					'causal_relationship', 'severity']
				for sKey in keysOfStr:
					if row[sKey] != '':
						previous_row[sKey] = previous_row[sKey] + separator + row[sKey]
				
				keysOfList = ['vaccinated_dates', 'onset_dates', 'PT_names', 'gross_result_dates', 'gross_results']
				for lKey in keysOfList:
					if len(row[lKey]) > 0 and ''.join(row[lKey]) != '':
						previous_row[lKey] += row[lKey]
				
				keysOfIntList = ['days_to_onset']
				for lKey in keysOfIntList:
					if len(row[lKey]) > 0:
						previous_row[lKey] += row[lKey]

			else:
				data.append(row)

	if len(data) != int(expected_count):
		print(f'[警告] 想定件数 {int(expected_count)}, 抽出した件数: {len(data)}')
	else:
		print(f'抽出した件数: {len(data)} 件')

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