import sys, json, os
import camelot

pdf_file_name = sys.argv[1]
pages = sys.argv[2]
vaccine_name = sys.argv[3]
source_dir = 'pdf-files'
output_dir = 'summary-data'

pdf_file_path = os.path.join(source_dir, pdf_file_name)
tables = camelot.read_pdf(pdf_file_path, pages=pages, encoding='utf-8')

numbers = {}
for table in tables:
    mydf = table.df
    alpha_row = mydf[mydf[0].str.contains('α')]
    if alpha_row.empty:
        continue
    alpha_row_index = alpha_row.index[0]
    numbers = { 
			"vaccine_name": vaccine_name,
			"evaluations": {
				"alpha": int(table.df.iloc[alpha_row_index,1].replace('件','').replace(',', '')),
				"beta": int(table.df.iloc[alpha_row_index+1,1].replace('件','').replace(',', '')),
				"gamma": int(table.df.iloc[alpha_row_index+2,1].replace('件','').replace(',', ''))
			}}

if not bool(numbers):
    print('「因果関係評価結果」の読み取りに失敗しました！')
    sys.exit(1)
    
json_string = json.dumps(numbers, ensure_ascii=False, indent=2)
file_name = pdf_file_name.rsplit('.', 1)[0]
output_path = os.path.join(output_dir, file_name + '.json')
with open( output_path, "w", encoding='utf-8') as f:
    f.write(json_string)