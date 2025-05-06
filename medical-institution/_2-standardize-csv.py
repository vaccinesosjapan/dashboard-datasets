import yaml, subprocess, os

with open('reports-settings.yaml', "r", encoding='utf-8') as file:
    settings = yaml.safe_load(file)

# 2. CSVデータを可能な限り整形する（手作業が残る箇所は、それとわかるようにログを出力する）
csv_file_name = f"{settings['file_id']}-pre.csv"
script_relative_path = os.path.join('.', settings["script-version"], "standardize-csv.py")

os.chdir('scripts')
print(f'{csv_file_name} のデータを整形します。手作業が必要な箇所についてログが出力されます。\n\n', end='', flush=True)
subprocess.run(["python", script_relative_path, settings['relative_dir'], csv_file_name, settings['has_concurrent_vaccination'] ])
print()
