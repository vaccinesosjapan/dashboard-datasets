import glob, json, os, sys, unicodedata
import yaml
import pandas as pd
sys.path.append("../libraries")
from exmedical import (
	create_graph_by_causal_relationship,
	create_graph_severities_of_related,
	cleansing_vaccine_name,
	create_unique_list,
	create_unique_list_with_2d_list
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
			d['vaccine_name'] = cleansing_vaccine_name(d['vaccine_name'])
			
			# manufacturer
			d['manufacturer'] = d['manufacturer'].replace('モデルナ／武\r\n田', 'モデルナ／武田')
			d['manufacturer'] = d['manufacturer'].replace('モデルナ／武\n田', 'モデルナ／武田')
			d['manufacturer'] = d['manufacturer'].replace('ノババックス\n／武田', 'ノババックス／武田')
			d['manufacturer'] = d['manufacturer'].replace('ノババックス\r\n／武田', 'ノババックス／武田')

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


# 症状などの一覧データを作って、ダッシュボードで表示するためのメタデータとして保存する処理
json_file_path = os.path.join(output_dir, 'medical-institution-reports.json')
df = pd.read_json(json_file_path)

certified_symptoms_metadata = {
	"gender_list": sorted(df['gender'].unique().tolist(), reverse=True),
	"vaccine_name_list": sorted( create_unique_list(df['vaccine_name'].unique().tolist()) ),
	"manufacturer_list": sorted( create_unique_list(df['manufacturer'].unique().tolist()) ),
	"causal_relationship_list": sorted( df['causal_relationship'].unique().tolist() , reverse=True),
	"severity_list": sorted(df['severity'].unique().tolist()),
	"gross_results_list": sorted( create_unique_list_with_2d_list(df['gross_results'].tolist()) ),
}
output_file_path = os.path.join(output_dir, 'medical-institution-metadata.json')
json_string = json.dumps(certified_symptoms_metadata, ensure_ascii=False, indent=2)
with open( output_file_path, "w", encoding='utf-8') as f:
	f.write(json_string)


# メタ情報と組み合わせつつ、抽出した事例一覧からいくつかの集計情報抽出を行う
sum_causal_relationship = create_graph_by_causal_relationship(sorted_issues)
sum_severities_of_related = create_graph_severities_of_related(sorted_issues)

valid_lotno_df = df[df['lot_no'].map(lambda x: not str(x).__contains__('不明') and str(x) != '99999')]

valid_lotno_dict = valid_lotno_df.groupby(['lot_no'])['no'].count().nlargest(10).to_dict()
valid_lotno_list = []
for k,v in valid_lotno_dict.items():
	valid_lotno_list.append({
		"lot_no": k,
		"count": v,
		"manufacturer": valid_lotno_df[valid_lotno_df['lot_no'] == k]['manufacturer'].unique()[0]
	})

moderna_lotno_dict = valid_lotno_df[valid_lotno_df['manufacturer'].str.contains('モデルナ')].groupby(['lot_no'])['no'].count().nlargest(10).to_dict()
moderna_lotno_list = []
for k,v in moderna_lotno_dict.items():
	moderna_lotno_list.append({
		"lot_no": k,
		"count": v,
		"manufacturer": valid_lotno_df[valid_lotno_df['lot_no'] == k]['manufacturer'].unique()[0]
	})

with open('summary-metadata.yaml', "r", encoding='utf-8') as file:
	metadata_root = yaml.safe_load(file)
metadata = metadata_root['metadata']

summary_data = {
	"medical_institution_summary_from_reports": {
		"date": metadata['issues']['date'],
		"total_count": len(sorted_issues),
		"sum_causal_relationship": sum_causal_relationship,
		"sum_severities_of_related": sum_severities_of_related,
		"lot_no_info": {
			"top_ten_list": valid_lotno_list,
			"top_ten_list_moderna": moderna_lotno_list,
			"invalid_count": df.shape[0] - valid_lotno_df.shape[0]
		},
	}
}

json_string = json.dumps(summary_data, ensure_ascii=False, indent=2)
output_path = os.path.join(output_dir, 'medical-institution-summary-from-reports.json')
with open( output_path, "w", encoding='utf-8') as f:
    f.write(json_string)