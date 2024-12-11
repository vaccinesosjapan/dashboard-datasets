import yaml, subprocess

with open('reports-settings.yaml', "r", encoding='utf-8') as file:
    settings_root = yaml.safe_load(file)
settings = settings_root['settings']

# 2. CSVデータを可能な限り整形する（手作業が残る箇所は、それとわかるようにログを出力する）
csv_file_name = f'{settings['file_id']}-{settings['symptoms']}.csv'
print(f'{csv_file_name} のデータを整形します。手作業が必要な箇所についてログが出力されます。', end='', flush=True)
subprocess.run(["python", f"standardize-csv.py", csv_file_name, settings['source']['name'], settings['source']['url'] ])
print()
