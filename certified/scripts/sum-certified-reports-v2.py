import glob, json, os, datetime, argparse
import pandas as pd
import yaml


def get_args():
    parser = argparse.ArgumentParser(description='Summarize judged issues')
    parser.add_argument('-s', '--source', metavar='source',
                        default='reports-data/*.json', help='Source directory to search json files')
    parser.add_argument('-o', '--output', metavar='output',
                        default='../_datasets', help='Target directory to save files')
    return parser.parse_args()


def create_reports(source: str) -> pd.DataFrame:
    '''
    ソースディレクトリからJSONファイルを全て読み込み、1つのDataFrameにして返す。
    '''
    json_file_list = glob.glob(source)
    reports = pd.DataFrame()

    for file in json_file_list:
        df = pd.read_json(file)
        reports = pd.concat([reports, df], ignore_index=True)

    # 元々は組み込みのsorted()を使ってlistをソートしていた。その時と同様の並びになるようstableソートを指定して使う。
    reports.sort_values(by=["certified_date"], kind='stable', ignore_index=True, inplace=True)
    # 第193回の分科会から、従来の予防接種と同じ表に列挙される案件が登場した。
    # これ以前のデータでは接種タイプ（inoculation_type）を区別していないため、ゼロ埋めする。
    reports['inoculation_type'] = reports['inoculation_type'].fillna(0).astype(int)
    reports.insert(0, 'no', range(1, reports.shape[0]+1))
    return reports


def save_df_to_json(df: pd.DataFrame, output_path: str) -> None:
    '''
    引数でもらったDataFrameを、可読性が高いフォーマットのJSONファイルへと保存する。
    '''
    json_str_org = df.to_json(orient='records', force_ascii=False)
    data = json.loads(json_str_org)
    json_string = json.dumps(data, ensure_ascii=False, indent=2)
    with open(output_path, "w", encoding='utf-8', newline="\n") as f:
        f.write(json_string)


def create_unique_symptoms_list(df: pd.DataFrame) -> list:
    '''
    symptoms 列のユニークな値をまとめたsetを返す。
    この列の各セルには文字列の配列が入っているため、それをフラットなlistにしてから処理が必要。
    '''
    symptoms_list = []
    df['symptoms'].map(lambda x: symptoms_list.extend(x))
    return list(set(symptoms_list))


def save_to_json(data, out_dir, filename):
	json_string = json.dumps(data, ensure_ascii=False, indent=2)
	output_path = os.path.join(out_dir, filename)
	with open( output_path, "w", encoding='utf-8', newline="\n") as f:
		f.write(json_string)


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


def main():
	args = get_args()
	output_dir = '../_datasets'

	# 抽出した認定・否認一覧をひとつにまとめてファイルに保存する。
	df = create_reports(args.source)
	output_path = os.path.join(args.output, 'certified-reports.json')
	save_df_to_json(df, output_path)

	certified_df = df[df['judgment_result'] == '認定']
	denied_df = df[df['judgment_result'] == '否認']
	certified_count = certified_df.shape[0]
	denied_count = denied_df.shape[0]    
	print(f'判定結果: {df["judgment_result"].unique()}')
	print(f'請求内容: {df['description_of_claim'].unique()}')
	print(f'否認理由: {sorted(df['reasons_for_repudiation'].str.join(',').unique())}')
	print(' -> 意図していない内容が含まれている場合は、データの調査が必要。')

	with open('summary-settings.yaml', "r", encoding='utf-8') as f:
		summary_settings_root = yaml.safe_load(f)
	summary_settings = summary_settings_root['settings']

	# 判定が「認定」の案件のみを対象として、症状ごとに性別で集計を実施する
	certified_df = df[df['judgment_result'] == '認定']
	unique_symptoms_list = create_unique_symptoms_list(certified_df)

	symptoms_names_dict = dict()
	for symptom in unique_symptoms_list:
		match_df = certified_df[certified_df['symptoms'].map(lambda x: symptom in x)]
		male_count = len(match_df[match_df['gender'] == "男"])
		female_count = len(match_df[match_df['gender'] == "女"])
		symptoms_names_dict[symptom] = { 
            'name': symptom,
            'counts': {'male': male_count, 'female': female_count, 'sum': male_count+female_count}
            }
	symptom_summary_list = sorted(list(symptoms_names_dict.values()), key=lambda issue: issue['name'])
	save_to_json(symptom_summary_list, args.output, 'certified-symptoms.json')

	certified_medical_count, certified_disability_children_count, certified_disability_count, certified_death_count = sum_with_description_of_claim(certified_df)
	denied_medical_count, denied_disability_children_count, denied_disability_count, denied_death_count = sum_with_description_of_claim(denied_df)

	# メタデータと判定結果一覧のデータから、「未処理件数」を算出する
	## [未処理件数] = [進達受理件数] - [認定件数] - [否認件数] - [保留件数]
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

	other_vaccines_df = pd.read_csv("other-vaccines/certified-issues-summary.csv", delimiter=',')
	covid19_vaccine_row = {'vaccine_name': "新型コロナ",
			'medical': certified_medical_count,
			'disability_of_children': certified_disability_children_count,
			'disability': certified_disability_count,
			'death': certified_death_count}
	other_vaccines_with_covid19_df = pd.concat([other_vaccines_df, pd.DataFrame(covid19_vaccine_row, index=[len(other_vaccines_df)])], ignore_index=True)


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
			"data": json.loads(other_vaccines_with_covid19_df.to_json(orient='records', force_ascii=False, indent=2))
		}
	}
	save_to_json(summary_with_other_vaccines, output_dir, 'certified-summary-with-other-vaccines.json')

	# 判定日などの一覧データを作成して、ダッシュボードで表示するためのメタデータとして保存する処理

	## '死亡一時金・葬祭料' というように、他の項目が内包された項目がある。
	## ダッシュボードで「◯◯を含む」という選択肢にしたいので、他の項目を含むものを除外する。
	claim_data = df['description_of_claim'].unique()
	claim_elements_list = []
	for item in claim_data:
		if not any((other in item and other != item) for other in claim_data):
			claim_elements_list.append(item)

	certified_metadata = {
		"judged_dates": sorted(list(df['certified_date'].unique()), reverse=True),
		"judged_result_list": sorted(list(df['judgment_result'].unique()), reverse=True),
		"gender_list": sorted(list(df['gender'].unique()), reverse=True),
		"claim_elements_list": sorted(claim_elements_list)
	}
	save_to_json(certified_metadata, output_dir, 'certified-metadata.json')

	# 症状などの一覧データを作成して、ダッシュボードで表示するためのメタデータとして保存する処理
	symptoms_df = pd.DataFrame(symptom_summary_list)
	certified_symptoms_metadata = {
		"symptom_name_list": sorted(list(symptoms_df['name'].unique())),
	}
	save_to_json(certified_symptoms_metadata, output_dir, 'certified-symptoms-metadata.json')


if __name__ == '__main__':
    main()