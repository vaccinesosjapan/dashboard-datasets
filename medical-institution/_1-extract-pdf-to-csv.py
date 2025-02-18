import yaml, subprocess, os, re

with open('reports-settings.yaml', "r", encoding='utf-8') as file:
    settings = yaml.safe_load(file)

# 1. PDFからデータを抽出し、CSVファイルに保存する
file_id_for_pdf = re.sub(r'-[0-9]*$', '', settings["file_id"])
pdf_file_name = f'{file_id_for_pdf}.pdf'
csv_file_name = f'{settings["file_id"]}.csv'

os.chdir('scripts')
print(f'"{pdf_file_name}" から抽出中\n\n', end='', flush=True)
subprocess.run([ "python", "extract-pdf-to-csv.py", settings['relative_dir'], pdf_file_name, csv_file_name, settings['pages'] ])
print()
