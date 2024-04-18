import yaml
import sys
import subprocess

if len(sys.argv) > 1:
    settings_file_path = sys.argv[1]
else:
    settings_file_path = 'summary-settings.yaml'

with open(settings_file_path, "r", encoding='utf-8') as file:
    settings_root = yaml.safe_load(file)
settings = settings_root['settings']

for s in settings:
    script_version = s['script-version'].lower()
    subprocess.run(["python", f"extract-death-summary-{script_version}.py", s['file'], s['pages'], s['name']])
