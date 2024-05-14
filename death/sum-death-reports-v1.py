import glob, json, os, sys
import yaml
import pandas as pd
sys.path.append("../libraries")
from exdeath import (
	create_graph_data_list_by_age
)

output_dir = '../_datasets'
death_issues = []

def convert_data(d):
	d['id'] = d['vaccine_name'] + '-' + str(d['no'])
	d['no'] = int(d['no'])
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
	return d


json_file_path_list = glob.glob('reports-data/*.json')
for json_file_path in json_file_path_list:
	with open(json_file_path, "r", encoding='utf-8') as f:
		data = json.load(f)
		for d in data:
			death_issues.append(convert_data(d))

json_file_path_list = glob.glob('intermediate-files/*.json')
for json_file_path in json_file_path_list:
	with open(json_file_path, "r", encoding='utf-8') as f:
		data = json.load(f)
		for d in data:
			death_issues.append(convert_data(d))


# 抽出した事例一覧の保存
sorted_issues = sorted(death_issues, key=lambda issue: issue['id'])
json_string = json.dumps(sorted_issues, ensure_ascii=False, indent=2)
output_path = os.path.join(output_dir, 'death-reports.json')
with open( output_path, "w", encoding='utf-8') as f:
    f.write(json_string)


# 性別などの一覧データを作成して、ダッシュボードで表示するためのメタデータとして保存する処理
json_file_path = os.path.join(output_dir, 'death-reports.json')
df = pd.read_json(json_file_path)
death_metadata = {
	"gender_list": sorted(df['gender'].unique().tolist(), reverse=True),
	# todo: 矢印などによるデータ修正に十分対応してから使うようにしたい
	# "causal_relationship_list": sorted(df['causal_relationship'].unique().tolist(), reverse=True),
	"causal_relationship_by_expert_list": sorted(df['causal_relationship_by_expert'].unique().tolist())
}
output_file_path = os.path.join(output_dir, 'death-metadata.json')
json_string = json.dumps(death_metadata, ensure_ascii=False, indent=2)
with open( output_file_path, "w", encoding='utf-8') as f:
	f.write(json_string)


# メタ情報と組み合わせつつ、抽出した事例一覧からいくつかの集計情報抽出を行う
with open('summary-metadata.yaml', "r", encoding='utf-8') as json_file_path:
    metadata_root = yaml.safe_load(json_file_path)
metadata = metadata_root['metadata']
sum_by_age = create_graph_data_list_by_age(sorted_issues)

## ロットNoの集計結果を保存する処理
invalid_lotno_df = df[df['lot_no'].map(lambda x: str(x).__contains__('不明') or not str(x))]
valid_lotno_df = df[df['lot_no'].map(lambda x: not str(x).__contains__('不明'))]

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

summary_data = {
	"death_summary_from_reports": {
		"date": metadata['issues']['date'],
		"sum_by_age": sum_by_age,
		"lot_no_info": {
			"top_ten_list": valid_lotno_list,
			"top_ten_list_moderna": moderna_lotno_list,
			"invalid_count": invalid_lotno_df.shape[0]
		},
	}
}

json_string = json.dumps(summary_data, ensure_ascii=False, indent=2)
output_path = os.path.join(output_dir, 'death-summary-from-reports.json')
with open( output_path, "w", encoding='utf-8') as f:
    f.write(json_string)