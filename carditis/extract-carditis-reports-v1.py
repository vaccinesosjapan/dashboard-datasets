import camelot
import json
import os
import sys
sys.path.append("../libraries")
from exfuncs import (
	extract_vaccine_name_etc,
	extract_age_gender,
	split_normal,
	extract_PT_names,
	split_pre_existing_disease_names
)

pdf_path = sys.argv[1]
pages = sys.argv[2]
source_name = sys.argv[3]
source_url = sys.argv[4]
tables = camelot.read_pdf(pdf_path, pages=pages, encoding='utf-8')

output_dir = 'reports-data'

data = []
for table in tables:
	rowCount, _ = table.df.shape
	for rowIndex in range(1, rowCount):
		row = table.df.loc[rowIndex]

		dto, vn, mf, ln, vt = extract_vaccine_name_etc(row[5], row[6])
		no, age, gender = extract_age_gender(row[0], row[1])
		
		onset_dates = split_normal(row[4])
		dNames = split_pre_existing_disease_names(row[7])
		PT_names = extract_PT_names(row[8])
		grd = split_normal(row[9])
		gr = split_normal(row[10])

		row = {
			"no": no,
			"age": age,
			"gender": gender,
			"vaccinated_date": row[3],
			"onset_dates": onset_dates,
			"days_to_onset": dto,
			"vaccine_name": vn,
			"manufacturer": mf,
			"lot_no": ln,
			"vaccinated_times": vt,
			"pre_existing_disease_names": dNames,
			"PT_names": PT_names,
			"gross_result_dates": grd,
			"gross_results": gr,
			"evaluated_PT": row[11],
			"evaluated_result": row[12],
			"brighton_classification": row[13],
			"expert_opinion": row[14].replace('\n',''),
			"remarks": row[15],
			"source": {
				"name": source_name,
				"url": source_url
			}
		}
		
		if row['no'] == '':
			previous_row = data[len(data)-1]
			separator = '\n'

			# sourceは結合不要
			keysOfStr = ['age', 'gender', 'vaccinated_date', 'days_to_onset', 'vaccine_name', 'manufacturer', 'lot_no',
				'vaccinated_times', 'evaluated_PT', 'evaluated_result', 'brighton_classification', 'expert_opinion', 'remarks']
			for sKey in keysOfStr:
				if row[sKey] != '':
					previous_row[sKey] = previous_row[sKey] + separator + row[sKey]
			
			keysOfList = ['onset_dates', 'pre_existing_disease_names', 'PT_names', 'gross_result_dates', 'gross_results']
			for lKey in keysOfList:
				if len(row[lKey]) > 0 and ''.join(row[lKey]) != '':
					previous_row[lKey] += row[lKey]

		else:
			data.append(row)

print(f'{len(data)} [件] 抽出しました')

json_string = json.dumps(data, ensure_ascii=False, indent=2)

file_name = pdf_path.rsplit('/', 1)[1]
output_path = os.path.join(output_dir, file_name + '.json')
with open( output_path, "w", encoding='utf-8') as f:
    f.write(json_string)