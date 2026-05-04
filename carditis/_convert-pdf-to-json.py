import yaml, subprocess, os, argparse


def get_args():
    """コマンドライン引数を取得する処理"""
 
    parser = argparse.ArgumentParser(description='実行内容を設定します')
    parser.add_argument('-j', '--json', default=False, help='JSON化の処理のみ行います')
    parser.add_argument('-s', '--script', default='v4', help='スクリプトのバージョンを指定します')
    return parser.parse_args()


def main():
    args = get_args()

    with open('reports-settings.yaml', "r", encoding='utf-8') as file:
        settings = yaml.safe_load(file)

    file_id = settings["file_id"]
    pdf_name = f'{file_id.split('-')[0]}.pdf'
    csv_name = f'{file_id}.csv'
    json_name = f"{file_id}.json"
    manufacturer = settings['manufacturer']
    pages = settings['pages']
    count = settings['count']
    source_name = settings['source']['name']
    source_url = settings['source']['url']

    script_version = args.script
    os.chdir('scripts')

    if not args.json:
        '''
        再評価時など、CSVの内容をあらかじめ手作業で再編集した上でJSON化だけ行いたい場合は、
        コマンドライン引数で「-j=True」を設定することでPDFからの抽出およびCSV化をスキップする。
        '''
        print('1. PDFからデータを抽出し、CSVファイルに保存します。')
        print(f'{settings["name"]} のデータを "{pdf_name}" から抽出中\n', end='', flush=True)
        subprocess.run([ "python", f"./{script_version}/extract-pdf-to-csv.py", file_id, pages])
        _ = input(f'./intermediate-files/{csv_name} の内容確認と修正が終わったら ENTER 押してください。')
        print()

        print('2. CSVデータを可能な限り整形し、どうしても手作業が残る箇所はログを出力します。')
        print(f'{csv_name} のデータを整形中\n', end='', flush=True)
        subprocess.run(["python", f"./{script_version}/standardize-csv.py", csv_name, manufacturer ])
        _ = input(f'./intermediate-files/{csv_name} の内容確認と修正が終わったら ENTER 押してください。')
        print()

    print('3. CSVデータをJSONデータへと書き出します。')
    print(f'手作業での修正が完了した {csv_name} に、最終的な整形を行ってJSONデータへと変換します。\n', end='', flush=True)
    subprocess.run([ "python", f"./{script_version}/export-to-json.py", csv_name, count, json_name, source_name, source_url ])
    print()


if __name__ == '__main__':
    main()