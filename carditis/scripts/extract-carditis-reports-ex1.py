import json, sys, math, os
import pandas as pd

csv_file_name = sys.argv[1]
source_name = sys.argv[3]
source_url = sys.argv[4]

csv_file_path = os.path.join('intermediate-files', csv_file_name)
df = pd.read_csv(csv_file_path, delimiter=',')

'''
ヘッダ：
  No,年齢,性別,接種日,発生日,接種から発生までの日数,ワクチン名,製造販売業者,ロット番号,接種回数,基礎疾患等,症状名（PT名）,転帰日,転帰内容,専門家の評価PT,専門家の因果関係評価,専門家のブライトン分類レベル,専門家の意見,備考
'''
data = []
for index, row in df.iterrows():
	rowData = {
		"no": row[0],
		"age": '' if isinstance(row[1], float) and math.isnan(row[1]) else row[1],
		"gender": '' if isinstance(row[2], float) and math.isnan(row[2]) else row[2],
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