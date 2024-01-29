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
for index, table in enumerate(tables):
	if table.df.iloc[1,0].find('α') > -1:
		numbers = { 
			"vaccine_name": vaccine_name,
			"evaluations": {
				"alpha": int(table.df.iloc[1,1].replace('件','').replace(',', '')),
				"beta": int(table.df.iloc[2,1].replace('件','').replace(',', '')),
				"gamma": int(table.df.iloc[3,1].replace('件','').replace(',', ''))
			}}

json_string = json.dumps(numbers, ensure_ascii=False, indent=2)

file_name = pdf_file_name.rsplit('.', 1)[0]
output_path = os.path.join(output_dir, file_name + '.json')
with open( output_path, "w", encoding='utf-8') as f:
    f.write(json_string)