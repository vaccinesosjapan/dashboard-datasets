import yaml, subprocess, os

with open('reports-settings.yaml', "r", encoding='utf-8') as file:
    settings = yaml.safe_load(file)

# 1. PDFからデータを抽出し、CSVファイルに保存する
pdf_file_name = f'{settings["file_id"]}.pdf'

os.chdir('scripts')
print(f'{settings["name"]} のデータを "{pdf_file_name}" から抽出中\n\n', end='', flush=True)
subprocess.run([ "python", f"extract-pdf-to-csv.py", pdf_file_name, settings['pages'], settings['symptoms'] ])
print()
