import glob, json, os
import pandas as pd

jsonFileList = glob.glob('reports-data/*.json')
output_dir = '../_datasets'

carditis_reports = []
for file in jsonFileList:
	with open(file, "r", encoding='utf-8') as f:
		data = json.load(f)
		carditis_reports += data

sorted_reports = sorted(carditis_reports, key=lambda issue: issue['no'])

# 心筋炎と心膜炎で重複している案件もあるため、noとvaccine_nameが同じものは
# 同一案件として片方だけを保存するようにする。
previous_no = 0
previous_vaccine_name = ''
reports_to_save = []
for report in sorted_reports:
	if previous_no == report['no'] and previous_vaccine_name == report['vaccine_name']:
		continue
	reports_to_save.append(report)
	previous_no = report['no']
	previous_vaccine_name = report['vaccine_name']

json_string = json.dumps(reports_to_save, ensure_ascii=False, indent=2)

output_path = os.path.join(output_dir, 'carditis-reports.json')
with open( output_path, "w", encoding='utf-8') as f:
    f.write(json_string)


# 性別などの一覧データを作成して、ダッシュボードで表示するためのメタデータとして保存する処理
json_file_path = os.path.join(output_dir, 'carditis-reports.json')
df = pd.read_json(json_file_path)
carditis_metadata = {
	"gender_list": sorted(df['gender'].unique().tolist(), reverse=True),
}
output_file_path = os.path.join(output_dir, 'carditis-metadata.json')
json_string = json.dumps(carditis_metadata, ensure_ascii=False, indent=2)
with open( output_file_path, "w", encoding='utf-8') as f:
	f.write(json_string)