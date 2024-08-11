import json, sys, math, os
import pandas as pd

sys.path.append("../libraries")
from exfuncs import (
	extract_PT_names,
)

csv_file_name = sys.argv[1]
source_name = sys.argv[3]
source_url = sys.argv[4]

csv_file_path = os.path.join('intermediate-files', csv_file_name)
df = pd.read_csv(csv_file_path, delimiter=',')

'''
あらかじめ手作業でcsvに保存するなどして修正・調整したうえで、そのcsvをjsonに変換するためのスクリプト。
camelotでPDFからデータを抽出し、dataframeのto_csvメソッドでcsv出力できるPDFなら楽。

例)
  tables = camelot.read_pdf('pdf-files/001280774.pdf', pages='7', encoding='utf-8')
  tables[0].df.to_csv('intermediate-files/001280774-myocarditis.csv',index=False, header=False, encoding='shift-jis')

ヘッダ：
  No,年齢,性別,接種日,発生日,接種から発生までの日数,ワクチン名,製造販売業者,ロット番号,基礎疾患等,症状名（PT名）,転帰日,転帰内容,専門家の評価PT,専門家の因果関係評価,専門家のブライトン分類レベル,専門家の意見,備考

ex1と比べると「接種回数」が無いヘッダ。
'''
data = []
for index, row in df.iterrows():
	# 先にNaNを空白文字列に変換しておく
	for index, cell in enumerate(row):
		if isinstance(cell, float):
			if math.isnan(cell):
				row[index] = ''
			else:
				row[index] = str(cell)

	ageRaw = row['年齢'].replace('歳', '')
	if ageRaw.isdecimal():
		age = int(ageRaw)
	else:
		age = ageRaw
	PT_Names = extract_PT_names(row['症状名（PT名）'])
	expertOpinionRaw = row['専門家の意見']
	expertOpinion = '' if isinstance(expertOpinionRaw, float) and math.isnan(expertOpinionRaw) else expertOpinionRaw.replace('\n', '')
	remarksRaw = row['備考']
	remarks = '' if isinstance(remarksRaw, float) and math.isnan(remarksRaw) else remarksRaw.replace('\n', '')

	rowData = {
		"no": row['No'],
		"age": age,
		"gender": row['性別'],
		"vaccinated_date": row['接種日'],
		"onset_dates": row['発生日'].split('\n'), 
		"days_to_onset": row['接種から発生までの日数'],
		"vaccine_name": row['ワクチン名'],
		"manufacturer": row['製造販売業者'],
		"lot_no": row['ロット番号'],
		"vaccinated_times": '', # データスキーマの互換性のため空文字を設定する
		"pre_existing_disease_names": row['基礎疾患等'].split(';\n'),
		"PT_names": PT_Names,
		"gross_result_dates": row['転帰日'].split('\n'),
		"gross_results": row['転帰内容'].split('\n'),
		"evaluated_PT": row['専門家の評価PT'],
		"evaluated_result": row['専門家の因果関係評価'],
		"brighton_classification": row['専門家のブライトン分類レベル'],
		"expert_opinion": expertOpinion,
		"remarks": remarks,
		"source": {
			"name": source_name,
			"url": source_url
		}
	}
	data.append(rowData)

print(f'{len(data)} [件] 抽出しました')

json_string = json.dumps(data, ensure_ascii=False, indent=2)
output_file_path = os.path.join('reports-data', csv_file_name.replace('.csv','.json'))
with open( output_file_path, "w", encoding='utf-8') as f:
	f.write(json_string)