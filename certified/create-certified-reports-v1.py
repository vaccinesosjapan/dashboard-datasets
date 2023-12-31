import yaml
import sys
import subprocess

if len(sys.argv) > 1:
    settings_file_path = sys.argv[1]
else:
    settings_file_path = 'reports-settings.yaml'

with open(settings_file_path, "r", encoding='utf-8') as file:
    settings_root = yaml.safe_load(file)
settings = settings_root['settings']

for s in settings:
    print(f'日付「{s["date"]}」のデータを抽出して {s["output"]} に保存中: ', end='', flush=True)
    script_version = s['script-version'].lower()
    certified_count = s['expected_count']['certified']
    repudiation_count = s['expected_count']['repudiation']
    subprocess.run([ "python", f"extract-certified-reports-{script_version}.py",
                    s['file'], s['output'], s['pages'], s['date'], s['reason-type'], f'{certified_count}', f'{repudiation_count}', s['source']['url'] ])
