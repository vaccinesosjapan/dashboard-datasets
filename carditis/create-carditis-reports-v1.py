import yaml, sys, subprocess

if len(sys.argv) > 1:
    settings_file_path = sys.argv[1]
else:
    settings_file_path = 'reports-settings.yaml'

with open('reports-settings.yaml', "r", encoding='utf-8') as file:
    settings_root = yaml.safe_load(file)
settings = settings_root['settings']

for s in settings:
    print(f'{s["name"]} のデータを "{s["file"]}" から抽出中: ', end='', flush=True)
    script_version = s['script-version'].lower()
    subprocess.run([ "python", f"extract-carditis-reports-{script_version}.py", s['file'], s['pages'], s['source']['name'], s['source']['url'] ])
    print()
