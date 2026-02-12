# %%
import glob, json, os
import pandas as pd
import yaml

jsonFileList = glob.glob('reports-data/*.json')
output_dir = '../_datasets'
metadata_file_path = os.path.join('metadata.yaml')

df = pd.DataFrame()
for file in jsonFileList:
	with open(file, "r", encoding='utf-8') as f:
		data = json.load(f)
		each_df = pd.DataFrame(data)
		df = pd.concat([df, each_df])


# %%
# id列を先頭にする操作と、id重複チェックを実施する。
start_with_id_columns = df.columns.delete(15).to_list()
start_with_id_columns.insert(0, "id")
df = df.reindex(columns=start_with_id_columns)
# ソートすると思ったような順番にならないため、あえてやらない。インデックスの振り直しだけ実施する。
df = df.reset_index(drop=True)

# idが重複している場合は、処理を中断して保存を行わない。
duplicated_df = df[df["id"].duplicated()].iloc[:, [0, 2, 3]]
if len(duplicated_df) > 0:
	print("[Error] idが重複したデータがあります。修正してください。")
	print(duplicated_df)
	exit(code=1)

# %%
# 亡くなった方の全症例をひとつにまとめて death-reports.json に保存する処理。
df_dict = df.to_dict("records")
json_string = json.dumps(df_dict, ensure_ascii=False, indent=2)

output_path = os.path.join(output_dir, 'death-reports.json')
with open( output_path, "w", encoding='utf-8') as f:
    f.write(json_string)

# %%
# 性別などの一覧データを作成して、ダッシュボードで表示するためのメタデータとして
# death-metadata.json に保存する処理。
death_metadata = {
	"gender_list": sorted(df['gender'].unique().tolist(), reverse=True),
	"causal_relationship_by_expert_list": sorted(df['causal_relationship_by_expert'].unique().tolist()),
}

json_string = json.dumps(death_metadata, ensure_ascii=False, indent=2)
output_file_path = os.path.join(output_dir, 'death-metadata.json')
with open( output_file_path, "w", encoding='utf-8') as f:
	f.write(json_string)

# %%
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

# %%
with open(metadata_file_path, "r", encoding='utf-8') as f:
    metadata_root = yaml.safe_load(f) 
metadata = metadata_root['metadata']

# %%
# 年齢に変な文字列が残っていないか確認するための処理
# df['age'].unique()

# %%
# XX歳代という情報を抽出するため、数字に変換されず文字列として残っている年齢データのうち
# 使えそうなデータだけを抽出する。
str_ages_series = df[df['age'].str.isdecimal().notna()]['age']
str_ages_series = str_ages_series.str.replace('歳代', '代').str.replace('代', '')
can_convert_ages_series = str_ages_series[str_ages_series.str.isdecimal()]
can_convert_ages_series = can_convert_ages_series.astype(int)

# %%
# もともと数字に変換できていた年齢データを抽出し、上述の変換データと結合する。
valid_ages_series = df[df['age'].astype(str).str.isdecimal()]['age']
valid_ages_series = pd.concat([valid_ages_series, can_convert_ages_series])

# %%
age_dict = { '0代': 0,  '10代': 0, '20代': 0, '30代': 0, '40代': 0, '50代': 0, '60代': 0, '70代': 0, '80代': 0, '90代': 0, '100歳以上': 0}
for age in valid_ages_series.values:
	if 0 <= age < 10:
		age_dict['0代'] += 1
	elif 10 <= age < 20:
		age_dict['10代'] += 1
	elif 20 <= age < 30:
		age_dict['20代'] += 1
	elif 30 <= age < 40:
		age_dict['30代'] += 1
	elif 40 <= age < 50:
		age_dict['40代'] += 1
	elif 50 <= age < 60:
		age_dict['50代'] += 1
	elif 60 <= age < 70:
		age_dict['60代'] += 1
	elif 70 <= age < 80:
		age_dict['70代'] += 1
	elif 80 <= age < 90:
		age_dict['80代'] += 1
	elif 90 <= age < 100:
		age_dict['90代'] += 1
	else:
		age_dict['100歳以上'] += 1

# %%
sum_by_age = []
for period in age_dict.keys():
	sum_by_age.append({"x": period, "y": age_dict[period]})

# %%
summary_data = {
	"death_summary_from_reports": {
		"date": metadata['data_end_date'],
		"ages_count": int(valid_ages_series.count()),
		"unknown_ages_count": int(df.shape[0] - valid_ages_series.count()),
		"sum_by_age": sum_by_age,
		"lot_no_info": {
			"top_ten_list": valid_lotno_list,
			"top_ten_list_moderna": moderna_lotno_list,
			"invalid_count": invalid_lotno_df.shape[0]
		},
	}
}

# %%
json_string = json.dumps(summary_data, ensure_ascii=False, indent=2)
output_path = os.path.join(output_dir, 'death-summary-from-reports.json')
with open( output_path, "w", encoding='utf-8') as f:
    f.write(json_string)

# %%
# 正解データであるdeath-table.csvの情報を集計して、ダッシュボードで使えるデータにする
expeced_df = pd.read_csv('death-table.csv')
expeced_df = expeced_df[expeced_df['Use']]
expeced_df = expeced_df.rename({'ワクチン名': 'vaccine_name'}, axis=1)
expeced_df = expeced_df.rename({'製造販売業者': 'manufacturer'}, axis=1)
result_series = expeced_df[['α', 'β', 'γ']].sum()

# %%
vaccine_name_grouped_df = expeced_df.groupby('vaccine_name')[['α', 'β', 'γ']].sum()
sum_by_vaccine_name = []
for vaccine_name in vaccine_name_grouped_df.index:
	sum_by_vaccine_name.append({
		"vaccine_name": vaccine_name,
		"evaluations": {
			"alpha": int(vaccine_name_grouped_df.loc[vaccine_name, 'α']),
        	"beta": int(vaccine_name_grouped_df.loc[vaccine_name, 'β']),
        	"gamma": int(vaccine_name_grouped_df.loc[vaccine_name, 'γ'])
		}
	})

# %%
manufacturer_grouped_df = expeced_df.groupby('manufacturer')[['α', 'β', 'γ']].sum()
manufacturer_grouped_series = (manufacturer_grouped_df['α'] + manufacturer_grouped_df['β'] + manufacturer_grouped_df['γ']).sort_values(ascending=False)
sum_by_manufacturer = []
for manufacturer in manufacturer_grouped_series.index:
	sum_by_manufacturer.append({"manufacturer": manufacturer, "death_count": int(manufacturer_grouped_series[manufacturer])})

# %%
death_summary = {
  "death_summary": {
    "date": metadata['commission_of_inquiry_date'],
    "source": {
      "name": metadata['source']['name'],
      "url": metadata['source']['url']
    },
    "sum_by_evaluation": {
      "total": int(result_series.sum()),
      "alpha": int(result_series['α']),
      "beta": int(result_series['β']),
      "gamma": int(result_series['γ'])
    },
    "sum_by_vaccine_name": sum_by_vaccine_name,
	  "sum_by_manufacturer": sum_by_manufacturer
  },
	"death_issues": {
    "date": metadata['data_end_date']
  }
}

# %%
json_string = json.dumps(death_summary, ensure_ascii=False, indent=2)
output_path = os.path.join(output_dir, 'death-summary.json')
with open( output_path, "w", encoding='utf-8') as f:
    f.write(json_string)


