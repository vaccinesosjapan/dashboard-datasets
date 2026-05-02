import yaml, subprocess, os


def main():
    '''
    3. 最終的な整形を行ったうえでJSON形式のファイルへと書き出す
    '''

    base_dir = os.getcwd()
    with open('reports-settings.yaml', "r", encoding='utf-8') as file:
        settings = yaml.safe_load(file)

    csv_file_name = f"{settings['file_id']}-manually-fixed.csv"
    count = settings['count']
    json_file_name = f"{settings['file_id']}.json"

    os.chdir('scripts')
    print(f'手作業で修正した {csv_file_name} のデータに最終的な整形を行ってJSONファイルへと出力します。\n\n', end='', flush=True)
    subprocess.run([ "python", f"./{settings['script_version']}/export-to-json.py", csv_file_name, count, json_file_name ])
    print()
    os.chdir(base_dir)
    

if __name__ == '__main__':
    main()