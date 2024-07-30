import sys, json, os, traceback, math, unicodedata, re
import pandas as pd

csv_file_name = sys.argv[1]
output_file_name = sys.argv[2]
# 第3引数のpagesは、このスクリプトでは不要
expected_count = sys.argv[4]
source_name = sys.argv[5]
source_url = sys.argv[6]
source_dir = 'intermediate-files'
output_dir = 'reports-data'

csv_file_path = os.path.join(source_dir, csv_file_name)
if not os.path.exists(csv_file_path):
	print(f'[エラー] csvファイル "{csv_file_path}" が見つかりません')
	sys.exit(1)
df = pd.read_csv(csv_file_path, delimiter=',')

'''
以下のような列ヘッダを持つデータを想定する。

  No,年齢,性別,接種日,発生日,接種から発生までの日数,ワクチン名,同時接種,製造販売業者,ロット番号,症状名（PT名）,因果関係（報告医評価）,重篤度（報告医評価）,転帰日,転帰内容

>>> >>> df.loc[0]
No                               40
年齢                              56歳
性別                               女性
接種日                       2022/6/21
発生日                       2022/6/23
接種から発生までの日数                       2
ワクチン名                     ヌバキソビッド筋注
同時接種                            NaN
製造販売業者                    ノババックス／武田
ロット番号                         99999
症状名（PT名）       アナフィラキシー（アナフィラキシー反応）
因果関係（報告医評価）                    関連あり
重篤度（報告医評価）                       重い
転帰日                        2022/9/1
転帰内容                             回復
'''
try:
	data = []
	for _, row in df.iterrows():
		# 先にNaNを空白文字列に変換しておく
		for index, cell in enumerate(row):
			if isinstance(cell, float):
				if math.isnan(cell):
					row[index] = ''
				else:
					# 否認理由が区切り文字ピリオドだった場合にもここにくるため、int型への
					# キャストは無しでstring型に変換する
					row[index] = str(cell)

		no = row['No']
		age = int(row['年齢'].replace('歳', ''))
		gender = row['性別']
		vaccinated_dates = row['接種日'].split('\n')
		onset_dates = row['発生日'].replace('\r\n', '\n').split('\n')
		days_to_onset = row['接種から発生までの日数']
		vaccine_name = row['ワクチン名']
		concurrent_vaccination = row['同時接種']
		manufacturer = row['製造販売業者']
		lot_no = row['ロット番号']

		PT_names = []
		matched = re.findall(r'(?<=（).*(?=）)', row['症状名（PT名）'])
		if matched:
			for m in matched:
				PT_names.append(m)
		
		causal_relationship = row['因果関係（報告医評価）']
		severity = row['重篤度（報告医評価）']
		gross_result_dates = row['転帰日'].replace('\r\n', '\n').split('\n')
		gross_results = row['転帰内容'].replace('\r\n', '\n').split('\n')

		row = {
			"no": no,
			"age": age,
			"gender": gender,
			"vaccinated_dates": row[3].split('\n'),
			"onset_dates": row[4].replace('\r\n', '\n').split('\n'),
			"days_to_onset": days_to_onset,
			"vaccine_name": vaccine_name,
			"concurrent_vaccination": row[7],
			"manufacturer": row[8],
			"lot_no": row[9],
			"PT_names": PT_names,
			"causal_relationship": row[11],
			"severity": row[12],
			"gross_result_dates": row[13].replace('\r\n', '\n').split('\n'),
			"gross_results": row[14].replace('\r\n', '\n').split('\n'),
			"source": {
				"name": source_name,
				"url": source_url
			}
		}

		data.append(row)

	if len(data) != int(expected_count):
		print(f'[警告] 想定件数 {int(expected_count)}, 抽出した件数: {len(data)}')
	else:
		print(f'抽出した件数: {len(data)} 件')
	
	json_string = json.dumps(data, ensure_ascii=False, indent=2)

	if not os.path.exists(output_dir):
		os.mkdir(output_dir)

	output_file_path = os.path.join(output_dir, output_file_name)
	with open( output_file_path, "w", encoding='utf-8') as f:
		f.write(json_string)

except Exception as e:
	print('Exception has occurred :-(')
	print("-"*60)
	print(f'name: {vaccine_name}, len(data): {len(data)}')
	print(f'row: {row}', file=sys.stderr)
	traceback.print_exc(file=sys.stderr)
	print("-"*60)
	print()
	sys.exit(1)