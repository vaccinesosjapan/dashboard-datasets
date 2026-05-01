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
    csv_file_name = f'{settings["file_id"]}.csv'
    script_relative_path = os.path.join('.', settings["script-version"], "extract-pdf-to-csv.py")

    os.chdir('scripts')
    print(f'"{pdf_file_name}" から抽出中\n\n', end='', flush=True)
    subprocess.run([ "python", script_relative_path, settings['relative_dir'], pdf_file_name, csv_file_name, settings['pages'] ])
    os.chdir(base_dir)
    
    converted_file_path = os.path.join('intermediate-files', settings['relative_dir'], f"{settings['file_id']}.csv")
    copy_file_name = f"{settings['file_id']}-pre.csv"
    copy_file_path = os.path.join('intermediate-files', settings['relative_dir'], copy_file_name)
    shutil.copyfile(converted_file_path, copy_file_path)
    print(f'{copy_file_path} を目視確認して手作業で微調整してください。')
    print()


if __name__ == '__main__':
    main()