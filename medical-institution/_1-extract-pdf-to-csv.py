import yaml, subprocess, os, re

with open('reports-settings.yaml', "r", encoding='utf-8') as file:
    settings = yaml.safe_load(file)

# 1. PDFからデータを抽出し、CSVファイルに保存する
pdf_file_name = f'{settings["file_id"]}.pdf'
csv_file_name = f'{settings["file_id"]}.csv'

os.chdir('scripts')
print(f'"{pdf_file_name}" から抽出中\n\n', end='', flush=True)
subprocess.run([ "python", "extract-pdf-to-csv.py", settings['relative_dir'], pdf_file_name, csv_file_name, settings['pages'] ])
print()
