import yaml, subprocess, os, shutil


def main():
    '''
    2. CSVデータを可能な限り整形する（手作業が残る箇所は、それとわかるようにログを出力する）
    '''

    base_dir = os.getcwd()
    with open('reports-settings.yaml', "r", encoding='utf-8') as file:
        settings = yaml.safe_load(file)

    file_id = settings['file_id']
    csv_file_name = f'{file_id}-pre.csv'
    manufacturer = settings['manufacturer']
    vaccine_name = settings['vaccine_name']
    has_vaccinated_times = settings['has_vaccinated_times']

    os.chdir('scripts')
    print(f'{csv_file_name} のデータを整形します。手作業が必要な箇所についてログが出力されます。\n\n', end='', flush=True)
    subprocess.run(["python", f"./{settings['script_version']}/standardize-csv.py", csv_file_name, manufacturer, vaccine_name, has_vaccinated_times ])
    print()
    os.chdir(base_dir)

    target_file_path = os.path.join('intermediate-files', f'{file_id}-converted.csv')
    copy_file_path = os.path.join('intermediate-files', f'{file_id}-manually-fixed.csv')
    shutil.copyfile(target_file_path, copy_file_path)
    print(f'{copy_file_path} を目視確認して手作業で微調整してください。')
    print()


if __name__ == '__main__':
    main()