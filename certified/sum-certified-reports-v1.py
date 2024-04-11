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

all_reports_json_string = json.dumps(sorted_reports, ensure_ascii=False, indent=2)
output_path = os.path.join(output_dir, 'certified-reports.json')
with open( output_path, "w", encoding='utf-8') as f:
    f.write(all_reports_json_string)


# 判定が「認定」の案件のみを対象として、症状ごとに性別で集計を実施する。
# 結果をファイルに保存する。
certified_symptoms_names_list = []
for item in sorted_reports:
	if item['judgment_result'] == '認定':
		certified_symptoms_names_list.extend(item['symptoms'])
certified_symptoms_names_set = set(certified_symptoms_names_list) # 一意な名前の一覧にする

certified_symptoms_names_dict = {s_name: { 'name': s_name, 'counts': {'male': 0, 'female': 0, 'sum': 0} } for s_name in certified_symptoms_names_set}
for item in sorted_reports:
	for symptom_name in item['symptoms']:
		# 空文字列の症状は保存されないような抽出にしているつもりなので、不要な読点「、」などがある
		# 元データの場合などの可能性あり。
		if symptom_name == "":
			print('[警告] 空白の症状名が抽出されているようです。以下の案件です。')
			print(item)
			print('-'*10)
			continue
			
		certified_symptoms_names_dict[symptom_name]['counts']['sum'] += 1
		if item['gender'] == '男':
			certified_symptoms_names_dict[symptom_name]['counts']['male'] += 1
		else:
			certified_symptoms_names_dict[symptom_name]['counts']['female'] += 1

symptom_summary_list = sorted(list(certified_symptoms_names_dict.values()), key=lambda issue: issue['name'])
symptom_summary_list_json_string = json.dumps(symptom_summary_list, ensure_ascii=False, indent=2)
output_path = os.path.join(output_dir, 'certified-symptoms.json')
with open( output_path, "w", encoding='utf-8') as f:
    f.write(symptom_summary_list_json_string)


# 認定・否認の件数に関して集計を行い、結果をファイルに保存する。
# 別途PDFから読み取って転記した集計情報も合わせて保存する。
certified_count = 0
denied_count = 0
certified_death_count = 0
denied_death_count = 0

for item in sorted_reports:
	if item['judgment_result'] == '認定':
		certified_count += 1
		if item['description_of_claim'].find('死') > -1 or item['description_of_claim'].find('葬') > -1:
			certified_death_count += 1
	elif item['judgment_result'] == '否認':
		denied_count += 1
		if item['description_of_claim'].find('死') > -1 or item['description_of_claim'].find('葬') > -1:
			denied_death_count += 1
	else:
		print(f'[警告] 認定と否認以外の判定結果が抽出されているようです')
		print(item)
		print('-'*10)

summary_settings_file_path = 'summary-settings.yaml'
with open(summary_settings_file_path, "r", encoding='utf-8') as file:
    summary_settings_root = yaml.safe_load(file)
summary_settings = summary_settings_root['settings']

open_cases_count = summary_settings['total_entries'] - certified_count - denied_count - summary_settings['pending_count']

certified_summary = {
	"date": summary_settings['date'],
	"total_entries": summary_settings['total_entries'],
	"certified_count": certified_count,
	"denied_count": denied_count,
	"pending_count": summary_settings['pending_count'],
	"open_cases_count": open_cases_count,
	"certified_death_count": certified_death_count,
	"denied_death_count": denied_death_count,
}
certified_summary_json = json.dumps(certified_summary, ensure_ascii=False, indent=2)
output_path = os.path.join(output_dir, 'certified-summary.json')
with open( output_path, "w", encoding='utf-8') as f:
    f.write(certified_summary_json)


# 過去のワクチン接種に関する認定一覧に、新型コロナワクチンの認定結果をマージして
# グラフ表示可能にするためのデータを作る処理。
medical_expenses_count = 0
disability_pension_of_children_count = 0
disability_pension_count = 0
death_count = 0

for item in sorted_reports:
	if item['judgment_result'] == '否認':
		continue
	
	claim = item['description_of_claim']
	if claim == '医療費・医療手当':
		medical_expenses_count += 1
	elif claim == '障害児養育年金':
		disability_pension_of_children_count += 1
	elif claim == '障害年金':
		disability_pension_count += 1
	elif claim.find('死亡一時金') > -1 or claim == '遺族年金' or claim == '遺族一時金' or claim.find('葬祭料') > -1:
		death_count += 1
	else:
		print('-'*10)
		print(f'unknown claim: {claim}')
		print('-'*10)

df = pd.read_csv("other-vaccines/certified-issues-summary.csv", delimiter=',')

new_row = {'vaccine_name': "新型コロナ",
		'medical': medical_expenses_count,
		'disability_of_children': disability_pension_of_children_count,
		'disability': disability_pension_count,
		'death': death_count}
df_added = pd.concat([df, pd.DataFrame(new_row, index=[len(df)])], ignore_index=True)

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
		"data": json.loads(df_added.to_json(orient='records', force_ascii=False, indent=2))
	}
}
json_string = json.dumps(summary_with_other_vaccines, ensure_ascii=False, indent=2)
output_file_path = os.path.join(output_dir, 'certified-summary-with-other-vaccines.json')
with open( output_file_path, "w", encoding='utf-8') as f:
	f.write(json_string)

# 判定日の一覧データを作成して、ダッシュボードで表示するためのメタデータとして保存する処理
json_file_path = os.path.join(output_dir, 'certified-reports.json')
df = pd.read_json(json_file_path)
certified_metadata = {
	"judged_dates": sorted(df['certified_date'].unique().tolist(), reverse=True)
}
output_file_path = os.path.join(output_dir, 'certified-metadata.json')
json_string = json.dumps(certified_metadata, ensure_ascii=False, indent=2)
with open( output_file_path, "w", encoding='utf-8') as f:
	f.write(json_string)