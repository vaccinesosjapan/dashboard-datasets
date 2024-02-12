import json, sys, math, os
import pandas as pd

csv_file_name = sys.argv[1]
source_name = sys.argv[3]
source_url = sys.argv[4]

csv_file_path = os.path.join('intermediate-files', csv_file_name)
df = pd.read_csv(csv_file_path, delimiter=',')

data = []
for index, row in df.iterrows():
	rowData = {
		"no": row[0],
		"age": row[1],
		"gender": row[2],
		"vaccinated_date": row[3],
		"onset_dates": row[4].split('\n'), 
		"days_to_onset": row[5],
		"vaccine_name": row[6],
		"manufacturer": row[7],
		"lot_no": row[8],
		"vaccinated_times": row[9],
		"pre_existing_disease_names": row[10].split(';\n'),
		"PT_names": row[11].split('\n'),
		"gross_result_dates": row[12].split('\n'),
		"gross_results": row[13].split('\n'),
		"evaluated_PT": row[14],
		"evaluated_result": row[15],
		"brighton_classification": row[16],
		"expert_opinion": '' if isinstance(row[17], float) and math.isnan(row[17]) else row[17].replace('\n', ''),
		"remarks": '' if isinstance(row[18], float) and math.isnan(row[18]) else row[18].replace('\n', ''),
		"source": {
			"name": source_name,
			"url": source_url
		}
	}
	data.append(rowData)

print(f'{len(data)} [件] 抽出しました')

json_string = json.dumps(data, ensure_ascii=False, indent=2)
output_file_path = os.path.join('reports-data', csv_file_name.replace('.csv','.json'))
with open( output_file_path, "w", encoding='utf-8') as f:
	f.write(json_string)