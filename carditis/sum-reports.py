import glob, json, os
import pandas as pd

jsonFileList = glob.glob('reports-data/*.json')
output_dir = '../_datasets'

carditis_reports = []
for file in jsonFileList:
	with open(file, "r", encoding='utf-8') as f:
		data = json.load(f)
		carditis_reports += data

# 心筋炎、心膜炎の全症例をひとつにまとめて carditis-reports.json に保存する処理。
## No列が「####」になっていてソートできないデータがあったので、3項演算子で大きな数字を返して末尾にする。
##  https://www.mhlw.go.jp/content/11120000/001325489.pdf#page=46
sorted_reports = sorted(carditis_reports, key=lambda issue: issue['no'] if isinstance(issue['no'], int) else 99999)

json_string = json.dumps(sorted_reports, ensure_ascii=False, indent=2)
output_path = os.path.join(output_dir, 'carditis-reports.json')
with open( output_path, "w", encoding='utf-8') as f:
    f.write(json_string)


# 性別などの一覧データを作成して、ダッシュボードで表示するためのメタデータとして
# carditis-metadata.json に保存する処理。
df = pd.DataFrame(sorted_reports)
carditis_metadata = {
	"gender_list": sorted(df['gender'].unique().tolist(), reverse=True),
}

json_string = json.dumps(carditis_metadata, ensure_ascii=False, indent=2)
output_file_path = os.path.join(output_dir, 'carditis-metadata.json')
with open( output_file_path, "w", encoding='utf-8') as f:
	f.write(json_string)


# ロットNoの集計結果を保存する処理。
valid_lotno_series = df['lot_no'].map(lambda x: not str(x).__contains__('不明'))
valid_lotno_df = df[valid_lotno_series]
invalid_lotno_df = df[~valid_lotno_series] # 先頭に「~」をつけるとbooleanが反転したSeriesを得られる

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