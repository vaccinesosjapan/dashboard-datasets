import glob
import json
import os

jsonFileList = glob.glob('reports-data/*.json')
output_dir = '../_datasets'

carditis_reports = []
for file in jsonFileList:
	with open(file, "r", encoding='utf-8') as f:
		data = json.load(f)
		carditis_reports += data

sorted_reports = sorted(carditis_reports, key=lambda issue: issue['no'])
json_string = json.dumps(sorted_reports, ensure_ascii=False, indent=2)

output_path = os.path.join(output_dir, 'carditis-reports.json')
with open( output_path, "w", encoding='utf-8') as f:
    f.write(json_string)