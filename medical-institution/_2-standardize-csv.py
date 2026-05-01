import yaml, subprocess, os, shutil


def main():
    '''
    2. CSVデータを可能な限り整形する（手作業が残る箇所は、それとわかるようにログを出力する）
    '''
    base_dir = os.getcwd()

    with open('reports-settings.yaml', "r", encoding='utf-8') as file:
        settings = yaml.safe_load(file)
    
    source_file_name = f"{settings['file_id']}-pre.csv"
    
    script_relative_path = os.path.join('.', settings["script-version"], "standardize-csv.py")

    os.chdir('scripts')
    print(f'{source_file_name} のデータを整形します。手作業が必要な箇所についてログが出力されます。\n\n', end='', flush=True)
    subprocess.run([ "python", script_relative_path, settings['relative_dir'], source_file_name, settings['has_concurrent_vaccination'], settings['id_metadata']['kind'] ])
    os.chdir(base_dir)

    converted_file_path = os.path.join('intermediate-files', settings['relative_dir'], f"{settings['file_id']}-converted.csv")
    copy_file_name = f"{settings['file_id']}-manually-fixed.csv"
    copy_file_path = os.path.join('intermediate-files', settings['relative_dir'], copy_file_name)
    shutil.copyfile(converted_file_path, copy_file_path)
    print(f'{copy_file_path} を目視確認して手作業で微調整してください。')
    print()


if __name__ == '__main__':
    main()