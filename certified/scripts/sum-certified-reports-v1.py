# %%
import glob, json, os, datetime
import pandas as pd
import yaml

json_file_list = glob.glob('reports-data/*.json')
output_dir = '../_datasets'

# 抽出した認定・否認一覧をひとつにまとめてファイルに保存する。
certified_reports = []
for file in json_file_list:
	with open(file, "r", encoding='utf-8') as f:
		data = json.load(f)
		certified_reports.extend(data)

sorted_reports = sorted(certified_reports, key=lambda issue: issue['certified_date'])
for index, repo_item in enumerate(sorted_reports):
	sorted_reports[index] = dict(**{'no': index+1}, **repo_item)

# %%
def save_to_json(data, out_dir, filename):
	json_string = json.dumps(data, ensure_ascii=False, indent=2)
	output_path = os.path.join(out_dir, filename)
	with open( output_path, "w", encoding='utf-8', newline="\n") as f:
		f.write(json_string)

# %%
def sum_with_description_of_claim(df):
	medical_expenses_count = df[df['description_of_claim'].str.contains('医療費・医療手当')].shape[0]
	disability_pension_of_children_count = df[df['description_of_claim'].str.contains('障害児養育年金')].shape[0]
	disability_pension_count = df[df['description_of_claim'].str.contains('障害年金')].shape[0]

	death_series = pd.Series([])
	death_claims = ['死亡一時金', '遺族年金', '遺族一時金', '葬祭料']
	for claim in death_claims:
		series = df[df['description_of_claim'].str.contains(claim)]['no']
		if death_series.count() == 0:
			death_series = series
		else:
			death_series = pd.concat([death_series, series])
	death_count = len(death_series.unique())

	return medical_expenses_count, disability_pension_of_children_count, disability_pension_count, death_count

# %%
# 全ての案件をひとつのファイルに保存する。
save_to_json(sorted_reports, output_dir, 'certified-reports.json')

# %%
df = pd.DataFrame(sorted_reports)
certified_df = df[df['judgment_result'] == '認定']
denied_df = df[df['judgment_result'] == '否認']

certified_count = certified_df.shape[0]
denied_count = denied_df.shape[0]

print(f'判定結果: {df["judgment_result"].unique()}')
print(f'請求内容: {df['description_of_claim'].unique()}')
print(f'否認理由: {sorted(df['reasons_for_repudiation'].map(lambda x: ','.join(x)).unique())}')
print(' -> 意図していない内容が含まれている場合は、データの調査が必要。')

# %%
with open('summary-settings.yaml', "r", encoding='utf-8') as f:
    summary_settings_root = yaml.safe_load(f)
summary_settings = summary_settings_root['settings']

# %%
# 判定が「認定」の案件のみを対象として、症状ごとに性別で集計を実施する
symptoms_list = []
certified_df['symptoms'].map(lambda x: symptoms_list.extend(x))
symptoms_unique_list = sorted(list(set(symptoms_list)))

symptoms_names_dict = {s_name: { 'name': s_name, 'counts': {'male': 0, 'female': 0, 'sum': 0} } for s_name in symptoms_unique_list}
for index in certified_df.index:
	symptoms = certified_df.loc[index, 'symptoms']
	gender = certified_df.loc[index, 'gender']

	for symptom_name in symptoms:
		if symptom_name == "":
			continue
			
		symptoms_names_dict[symptom_name]['counts']['sum'] += 1
		if  gender == '男':
			symptoms_names_dict[symptom_name]['counts']['male'] += 1
		elif gender == '女':
			symptoms_names_dict[symptom_name]['counts']['female'] += 1
		else:
			print(f'性別が不明かも {gender}')
symptom_summary_list = sorted(list(symptoms_names_dict.values()), key=lambda issue: issue['name'])

save_to_json(symptom_summary_list, output_dir, 'certified-symptoms.json')

# %%
certified_medical_count, certified_disability_children_count, certified_disability_count, certified_death_count = sum_with_description_of_claim(certified_df)
denied_medical_count, denied_disability_children_count, denied_disability_count, denied_death_count = sum_with_description_of_claim(denied_df)

# %%
# メタデータと判定結果一覧のデータから、「未処理件数」を算出する
## [未処理件数] = [進達受理件数] - [認定件数] - [否認件数] - [保留件数]
open_cases_count = summary_settings['total_entries'] - certified_count - denied_count - summary_settings['pending_count']

# %%
certified_summary = {
	"date": summary_settings['date'],
	"total_entries": summary_settings['total_entries'],
	"certified_count": certified_count,
	"denied_count": denied_count,
	"pending_count": summary_settings['pending_count'],
	"open_cases_count": open_cases_count,
	"certified_death_count": certified_death_count,
	"denied_death_count": denied_death_count,
	"certified_counts": [
		{
			"name": "medical_expenses",
			"count": certified_medical_count
		},
		{
			"name": "disability_pension_of_children",
			"count": certified_disability_children_count
		},
		{
			"name": "disability_pension",
			"count": certified_disability_count
		},
		{
			"name": "death",
			"count": certified_death_count
		}
	],
	"denied_counts": [
		{
			"name": "medical_expenses",
			"count": denied_medical_count
		},
		{
			"name": "disability_pension_of_children",
			"count": denied_disability_children_count
		},
		{
			"name": "disability_pension",
			"count": denied_disability_count
		},
		{
			"name": "death",
			"count": denied_death_count
		}
	]
}
save_to_json(certified_summary, output_dir, 'certified-summary.json')

# %%
other_vaccines_df = pd.read_csv("other-vaccines/certified-issues-summary.csv", delimiter=',')
covid19_vaccine_row = {'vaccine_name': "新型コロナ",
		'medical': certified_medical_count,
		'disability_of_children': certified_disability_children_count,
		'disability': certified_disability_count,
		'death': certified_death_count}
other_vaccines_with_covid19_df = pd.concat([other_vaccines_df, pd.DataFrame(covid19_vaccine_row, index=[len(other_vaccines_df)])], ignore_index=True)

# %%
with open('reports-settings-all.yaml', "r", encoding='utf-8') as file:
    settings_root = yaml.safe_load(file)
settings = settings_root['settings']

date_format = '%Y/%m/%d'
first_date = datetime.datetime.today()
last_date = datetime.datetime.strptime('2021/01/01', date_format)

for setting in settings:
    dt = datetime.datetime.strptime(setting['date'], date_format)
    if dt > last_date:
        last_date = dt
    if dt < first_date:
        first_date = dt

span_year = 0
span_month = 0
if last_date.month - first_date.month < 0:
	span_year = last_date.year - first_date.year - 1
	span_month = 12 + last_date.month - first_date.month
else:
	span_year = last_date.year - first_date.year
	span_month = last_date.month - first_date.month


with open('other-vaccines/metadata.yaml', "r", encoding='utf-8') as file:
    metadata_root = yaml.safe_load(file)
metadata = metadata_root['metadata']

date_format2 = '%Y/%m'
f_date = datetime.datetime.strptime(metadata['first_date'], date_format2)
l_date = datetime.datetime.strptime(metadata['last_date'], date_format2)

s_year = 0
s_month = 0
if l_date.month - f_date.month < 0:
	s_year = l_date.year - f_date.year - 1
	s_month = 12 + l_date.month - f_date.month
else:
	s_year = l_date.year - f_date.year
	s_month = l_date.month - f_date.month

# %%
summary_with_other_vaccines = {
	"meta_data": {
		"covid19_vaccine": {
			"first_date": first_date.strftime('%Y/%m/%d'),
			"last_date": last_date.strftime('%Y/%m/%d'),
			"period": f'{span_year}年{span_month}ヶ月',
			"certified_count": certified_count,
			"source_url": "https://www.mhlw.go.jp/stf/shingi/shingi-shippei_127696_00001.html"
		},
		"other_vaccines": {
			"first_date": metadata['first_date'],
			"last_date": metadata['last_date'],
			"period": f'{s_year}年{s_month}ヶ月',
			"certified_count": int(metadata['certified_count']),
			"source_url": metadata['source_url']
		}
	},
	"chart_data": {
		"headers": ['ワクチン名', '医療費・医療手当', '障害児養育年金', '障害年金', '死亡一時金・遺族年金・遺族一時金・葬祭料'],
		"data": json.loads(other_vaccines_with_covid19_df.to_json(orient='records', force_ascii=False, indent=2))
	}
}
save_to_json(summary_with_other_vaccines, output_dir, 'certified-summary-with-other-vaccines.json')

# %%
# 判定日などの一覧データを作成して、ダッシュボードで表示するためのメタデータとして保存する処理

## '死亡一時金・葬祭料' というように、他の項目が内包された項目がある。
## ダッシュボードで「◯◯を含む」という選択肢にしたいので、他の項目を含むものを除外する。
claim_data = df['description_of_claim'].unique()
claim_elements_list = []
for item in claim_data:
    if not any((other in item and other != item) for other in claim_data):
        claim_elements_list.append(item)

certified_metadata = {
	"judged_dates": sorted(df['certified_date'].unique().tolist(), reverse=True),
	"judged_result_list": sorted(df['judgment_result'].unique().tolist(), reverse=True),
	"gender_list": sorted(df['gender'].unique().tolist(), reverse=True),
	"claim_elements_list": sorted(claim_elements_list)
}
save_to_json(certified_metadata, output_dir, 'certified-metadata.json')

# %%
# 症状などの一覧データを作成して、ダッシュボードで表示するためのメタデータとして保存する処理
symptoms_df = pd.DataFrame(symptom_summary_list)
certified_symptoms_metadata = {
	"symptom_name_list": sorted(symptoms_df['name'].unique().tolist()),
}
save_to_json(certified_symptoms_metadata, output_dir, 'certified-symptoms-metadata.json')
