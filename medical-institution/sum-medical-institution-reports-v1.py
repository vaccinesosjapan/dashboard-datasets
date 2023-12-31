import glob, json, os, sys
import yaml
sys.path.append("../libraries")
from exmedical import (
	create_graph_by_causal_relationship,
	create_graph_severities_of_related,
	create_keys,
	create_keys_from_array
)

jsonFileList = glob.glob('reports-data/*.json')
output_dir = '../_datasets'

medical_institution_issues = []
for file in jsonFileList:
	with open(file, "r", encoding='utf-8') as f:
		data = json.load(f)
		for d in data:
			if type(d['no']) == type(''):
				dNo = d['no']
				dNo = dNo.split('\n')[0]
				dNo = dNo.split('注')[0]
				dNo = dNo.split('※')[0]
				dNo = dNo.split('→')[0]
				d['no'] = int(dNo)
			
			# vaccine_name
			d['vaccine_name'] = d['vaccine_name'].replace('\n歳用', '歳用')
			d['vaccine_name'] = d['vaccine_name'].replace('歳\n用', '歳用')
			d['vaccine_name'] = d['vaccine_name'].replace('２\n価', '２価')
			d['vaccine_name'] = d['vaccine_name'].replace('価\n不明', '価不明')
			d['vaccine_name'] = d['vaccine_name'].replace('\n起源株', '起源株')
			d['vaccine_name'] = d['vaccine_name'].replace('起\n源株', '起源株')
			d['vaccine_name'] = d['vaccine_name'].replace('起源\n株', '起源株')
			d['vaccine_name'] = d['vaccine_name'].replace('株\nBA.1', '株BA.1')
			d['vaccine_name'] = d['vaccine_name'].replace('BA.4-\n5', 'BA.4-5')
			d['vaccine_name'] = d['vaccine_name'].replace('11歳用\n（', '11歳用（')
			d['vaccine_name'] = d['vaccine_name'].replace('オミクロ\nン', 'オミクロン')
			
			# manufacturer
			d['manufacturer'] = d['manufacturer'].replace('モデルナ／武\n田', 'モデルナ／武田')
			d['manufacturer'] = d['manufacturer'].replace('ノババックス\n／武田', 'ノババックス／武田')

			for i, osd in enumerate(d['onset_dates']):
				d['onset_dates'][i] = osd.strip()
			for i, grd in enumerate(d['gross_result_dates']):
				d['gross_result_dates'][i] = grd.strip()
			for i, gr in enumerate(d['gross_results']):
				d['gross_results'][i] = gr.strip()
			medical_institution_issues.append(d)

# 抽出した事例一覧の保存
sorted_issues = sorted(medical_institution_issues, key=lambda issue: issue['no'])
json_string = json.dumps(sorted_issues, ensure_ascii=False, indent=2)
output_path = os.path.join(output_dir, 'medical-institution-reports.json')
with open( output_path, "w", encoding='utf-8' ) as f:
	f.write(json_string)

# メタ情報と組み合わせつつ、抽出した事例一覧からいくつかの集計情報抽出を行う
with open('summary-metadata.yaml', "r", encoding='utf-8') as file:
	metadata_root = yaml.safe_load(file)
metadata = metadata_root['metadata']

sum_causal_relationship = create_graph_by_causal_relationship(sorted_issues)
sum_severities_of_related = create_graph_severities_of_related(sorted_issues)

summary_data = {
	"medical_institution_summary_from_reports": {
		"date": metadata['issues']['date'],
		"total_count": len(sorted_issues),
		"sum_causal_relationship": sum_causal_relationship,
		"sum_severities_of_related": sum_severities_of_related
	}
}

json_string = json.dumps(summary_data, ensure_ascii=False, indent=2)
output_path = os.path.join(output_dir, 'medical-institution-summary-from-reports.json')
with open( output_path, "w", encoding='utf-8') as f:
    f.write(json_string)

#どんな項目があるのかという一覧を作ろうとした処理
keys_of_vaccine_name = create_keys(sorted_issues, 'vaccine_name')
keys_of_manufacturer = create_keys(sorted_issues, 'manufacturer')
keys_of_causal_relationship = create_keys(sorted_issues, 'causal_relationship')
keys_of_severity = create_keys(sorted_issues, 'severity')
keys_of_gross_results = create_keys_from_array(sorted_issues, 'gross_results')

keys_data = {
	"vaccine_name": keys_of_vaccine_name,
	"manufacturer": keys_of_manufacturer,
	"causal_relationship": keys_of_causal_relationship,
	"severity": keys_of_severity,
	"gross_results": keys_of_gross_results
}

json_string = json.dumps(keys_data, ensure_ascii=False, indent=2)
output_path = os.path.join(output_dir, 'medical-institution-keys-of-reports.json')
with open( output_path, "w", encoding='utf-8') as f:
    f.write(json_string)
