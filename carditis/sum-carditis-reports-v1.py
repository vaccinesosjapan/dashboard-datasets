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


def delete_duplecates(reports):
	# 心筋炎と心膜炎で重複している案件もあるため、noとvaccine_nameが同じものは
	# 同一案件とみなして片方だけを保存するようにする、という処理をかつては使っていた。
	previous_no = 0
	previous_vaccine_name = ''
	deleted_duplecates_reports = []
	for report in sorted_reports:
		if previous_no == report['no'] and previous_vaccine_name == report['vaccine_name']:
			continue
		deleted_duplecates_reports.append(report)
		previous_no = report['no']
		previous_vaccine_name = report['vaccine_name']
	return deleted_duplecates_reports


# json_string = json.dumps(delete_duplecates(sorted_reports), ensure_ascii=False, indent=2)
json_string = json.dumps(sorted_reports, ensure_ascii=False, indent=2)

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


# ロットNoの集計結果を保存する処理
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
	"carditis_summary_from_reports": {
		"lot_no_info": {
			"top_ten_list": valid_lotno_list,
			"top_ten_list_moderna": moderna_lotno_list,
			"invalid_count": invalid_lotno_df.shape[0]
		},
	}
}

json_string = json.dumps(summary_data, ensure_ascii=False, indent=2)
output_path = os.path.join(output_dir, 'carditis-summary-from-reports.json')
with open( output_path, "w", encoding='utf-8') as f:
    f.write(json_string)