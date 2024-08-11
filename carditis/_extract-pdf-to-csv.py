import sys, os
import camelot

pdf_file_name = sys.argv[1]
pages = sys.argv[2]
pdf_file_path = os.path.join('pdf-files', pdf_file_name)

tables = camelot.read_pdf(pdf_file_path, pages=pages, encoding='utf-8')
index = 1
for table in tables:
	csv_file_path = os.path.join('extracted-csv-files', pdf_file_name.replace('.pdf',f'-{index}.csv'))
	table.df.to_csv(csv_file_path, index=False, header=False, encoding='utf-8')