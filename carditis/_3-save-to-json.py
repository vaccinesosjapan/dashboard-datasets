import yaml, subprocess

with open('reports-settings.yaml', "r", encoding='utf-8') as file:
    settings_root = yaml.safe_load(file)
settings = settings_root['settings']

# 3. 最終的な整形を行ったうえでJSON形式のファイルへと書き出す
# 先の手順の結果として f'{settings['file_id']}-{settings['symptoms']}-converted.csv' というファイルが出力される。
# これに対して手作業で修正を行って f'{settings['file_id']}-{settings['symptoms']}-manually-fixed.csv' という名前で保存した前提で作業する。
csv_file_name = f'{settings['file_id']}-{settings['symptoms']}-manually-fixed.csv'
print(f'手作業で修正した {csv_file_name} のデータに最終的な整形を行ってJSONファイルへと出力します。', end='', flush=True)
subprocess.run([ "python", f"export-to-json.py", csv_file_name, settings['count'] ])
print()