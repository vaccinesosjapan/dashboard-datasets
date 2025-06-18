import glob, json, os, re
import pandas as pd

jsonFileList = glob.glob('reports-data/*.json')
output_dir = '../_datasets'

re_carditis_type = re.compile(r"[0-9]-(?P<type>.*?).json")
df = pd.DataFrame()
for json_file_path in jsonFileList:
	matched = re_carditis_type.search(json_file_path.replace('reports-data/', ''))
	with open(json_file_path, "r", encoding='utf-8') as f:
		data = json.load(f)
		each_df = pd.DataFrame(data)
		each_df['carditis_type'] = matched.group('type')
		df = pd.concat([df, each_df])


class IncrementNumber:
	counter = 0

	def count_up(self):
		self.counter = self.counter + 1
		return self.counter


source_df = df['source'].apply(pd.Series)
source_df['prefix'] = source_df['name'].str.replace('第', '').str.replace('回', '')
increment_number = IncrementNumber()
## No列が「####」になっているデータは、「X00001」というようにプレフィックスXをつけた連番を生成してID生成に用いる
df['id'] = source_df['prefix'] + '-' + df['carditis_type'] + '-' + df['no'].map(lambda x: '{:0=6}'.format(x) if isinstance(x, int) else 'x' + '{:0=5}'.format(increment_number.count_up()))
df = df.drop('carditis_type', axis=1)
df = df.sort_values('id')


# 心筋炎、心膜炎の全症例をひとつにまとめて carditis-reports.json に保存する処理。
##  https://www.mhlw.go.jp/content/11120000/001325489.pdf#page=46
df_dict = df.to_dict("records")
json_string = json.dumps(df_dict, ensure_ascii=False, indent=2)

output_path = os.path.join(output_dir, 'carditis-reports.json')
with open( output_path, "w", encoding='utf-8') as f:
    f.write(json_string)


# 性別などの一覧データを作成して、ダッシュボードで表示するためのメタデータとして
# carditis-metadata.json に保存する処理。
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