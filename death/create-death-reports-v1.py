import yaml
import sys
import subprocess

if len(sys.argv) > 1:
    settings_file_path = sys.argv[1]
else:
    settings_file_path = 'reports-settings-all.yaml'

with open(settings_file_path, "r", encoding='utf-8') as file:
    settings_root = yaml.safe_load(file)
settings = settings_root['settings']

for s in settings:
    print(f'{s["name"]} のデータを "{s["file"]}" から {s["output"]} へ抽出中: ', end='', flush=True)
    script_version = s['script-version'].lower()
    subprocess.run(["python", f"extract-death-reports-{script_version}.py",
                    s['file'], s['output'], s['pages'], s['manufacturer'], s['name']])
