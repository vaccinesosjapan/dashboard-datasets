import yaml, subprocess

with open('reports-settings.yaml', "r", encoding='utf-8') as file:
    settings_root = yaml.safe_load(file)
settings = settings_root['settings']

# 1. PDFからデータを抽出し、CSVファイルに保存する
print(f'{settings["name"]} のデータを "{settings["file"]}" から抽出中: ', end='', flush=True)
subprocess.run([ "python", f"extract-pdf-to-csv.py", f'{settings['file_id']}.pdf', settings['pages'], settings['symptoms'] ])
print()
