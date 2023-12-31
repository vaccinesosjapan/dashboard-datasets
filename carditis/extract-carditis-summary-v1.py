import sys
import camelot
import json
import os

pdf_path = sys.argv[1]
pages = sys.argv[2]
vaccine_name = sys.argv[3]
tables = camelot.read_pdf(pdf_path, pages=pages, encoding='utf-8')

output_dir = 'summary-data'

def __extract_row__(df):
	if len(df) < 3:
		raise ValueError(f'Summary table should have 3 or more rows. this table only {len(df)} rows')
	
	row = []
	if len(table.df.loc[2]) == 1:
		# たまに列の分割がうまくいかないケースがあるため
		row = table.df.iloc[2,0].split('\n')
	else:
		row = table.df.loc[2]

	return row

myocarditis_count = 0
pericarditis_count = 0
for index, table in enumerate(tables):
	if index == 1:
		row = __extract_row__(table.df)
		myocarditis_count = int(row[3])
	elif index == 2:
		row = __extract_row__(table.df)
		pericarditis_count = int(row[3])

issue = {
	"vaccine_name": vaccine_name,
	"myocarditis_count": myocarditis_count,
	"pericarditis_count": pericarditis_count
}

print(f'[心筋炎 {issue["myocarditis_count"]} 件], [心膜炎 {issue["pericarditis_count"]} 件] 抽出しました')

json_string = json.dumps(issue, ensure_ascii=False, indent=2)

file_name = pdf_path.rsplit('/', 1)[1]
output_path = os.path.join(output_dir, file_name + '.json')
with open( output_path, "w", encoding='utf-8') as f:
    f.write(json_string)