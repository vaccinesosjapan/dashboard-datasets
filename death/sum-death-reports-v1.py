import glob, json, os, sys
import yaml
sys.path.append("../libraries")
from exdeath import (
	create_graph_data_list_by_age
)

jsonFileList = glob.glob('reports-data/*.json')
output_dir = '../_datasets'

death_issues = []
for file in jsonFileList:
	with open(file, "r", encoding='utf-8') as f:
		data = json.load(f)
		for d in data:
			d['id'] = d['vaccine_name'] + '-' + d['no']
			dNo = d['no']
			dNo = dNo.split('\n')[0]
			dNo = dNo.split('注')[0]
			dNo = dNo.split('※')[0]
			dNo = dNo.split('→')[0]

			if(dNo == ''):
				# ここでdNoが空になる抽出データは、どこか別件に統合されたデータなので
				# このマージ処理で除外する
				continue
			else:
				d['no'] = int(dNo)
				d['vaccinated_dates'] = d['vaccinated_dates'].replace('年', '/').replace('月', '/').replace('日', '')
				dAge = d['age']
				dAge = dAge.split('\n')[0]
				dAge = dAge.split('※')[0]
				dAge = dAge.replace('歳', '')
				if dAge.isdecimal():
					d['age'] = int(dAge)
				else:
					d['age'] = dAge
				onset_dates = d['onset_dates']
				for dIndex, day in enumerate(onset_dates):
					onset_dates[dIndex] = day.replace('年', '/').replace('月', '/').replace('日', '')
				death_issues.append(d)

# 抽出した事例一覧の保存
sorted_issues = sorted(death_issues, key=lambda issue: issue['id'])
json_string = json.dumps(sorted_issues, ensure_ascii=False, indent=2)
output_path = os.path.join(output_dir, 'death-reports.json')
with open( output_path, "w", encoding='utf-8') as f:
    f.write(json_string)

# メタ情報と組み合わせつつ、抽出した事例一覧からいくつかの集計情報抽出を行う
with open('summary-metadata.yaml', "r", encoding='utf-8') as file:
    metadata_root = yaml.safe_load(file)
metadata = metadata_root['metadata']

sum_by_age = create_graph_data_list_by_age(sorted_issues)

summary_data = {
	"death_summary_from_reports": {
		"date": metadata['issues']['date'],
		"sum_by_age": sum_by_age
	}
}

json_string = json.dumps(summary_data, ensure_ascii=False, indent=2)
output_path = os.path.join(output_dir, 'death-summary-from-reports.json')
with open( output_path, "w", encoding='utf-8') as f:
    f.write(json_string)