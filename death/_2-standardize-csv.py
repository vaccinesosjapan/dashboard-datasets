import yaml, subprocess, os

with open('reports-settings.yaml', "r", encoding='utf-8') as file:
    settings = yaml.safe_load(file)

# 2. CSVデータを可能な限り整形する（手作業が残る箇所は、それとわかるようにログを出力する）
file_id = settings['file_id']
csv_file_name = f'{file_id}-pre.csv'
manufacturer = settings['manufacturer']
vaccine_name = settings['vaccine_name']
has_vaccinated_times = settings['has_vaccinated_times']

os.chdir('scripts')
print(f'{csv_file_name} のデータを整形します。手作業が必要な箇所についてログが出力されます。\n\n', end='', flush=True)
subprocess.run(["python", f"./{settings['script_version']}/standardize-csv.py", csv_file_name, manufacturer, vaccine_name, has_vaccinated_times ])
print()
