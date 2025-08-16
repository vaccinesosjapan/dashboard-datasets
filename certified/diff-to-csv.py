import os, subprocess

script_dir = os.path.dirname(os.path.abspath(__file__))
save_to_csv_path = os.path.join(script_dir, 'scripts', 'save-to-csv.py')

# diff.txt には、CSVファイルが無くJSONだけあるファイル名（拡張子無し）を列挙して記載する。
with open('diff.txt', 'r', encoding='utf-8') as f:
	for line in f:
		subprocess.run(['python', save_to_csv_path, line.strip()], cwd=script_dir)