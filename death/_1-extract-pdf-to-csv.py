import yaml, subprocess, os, re, shutil

 
def main():
    '''
    1. PDFからデータを抽出し、CSVファイルに保存する
    '''

    base_dir = os.getcwd()
    with open('reports-settings.yaml', "r", encoding='utf-8') as file:
        settings = yaml.safe_load(file)

    file_id_for_pdf = re.sub(r'-[0-9]*$', '', settings["file_id"])
    pdf_file_name = f'{file_id_for_pdf}.pdf'
    target_file_name = f'{settings["file_id"]}.csv'

    os.chdir('scripts')
    print(f'{settings["vaccine_name"]} のデータを "{pdf_file_name}" から抽出中\n\n', end='', flush=True)
    subprocess.run([ "python", f"./{settings['script_version']}/extract-pdf-to-csv.py", pdf_file_name, target_file_name, settings['pages'] ])
    print()
    os.chdir(base_dir)

    target_file_path = os.path.join('intermediate-files', target_file_name)
    copy_file_path = os.path.join('intermediate-files', f'{settings["file_id"]}-pre.csv')
    shutil.copyfile(target_file_path, copy_file_path)
    print(f'{copy_file_path} を目視確認して手作業で微調整してください。')
    print()


if __name__ == '__main__':
    main()
