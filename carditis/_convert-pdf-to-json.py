import yaml, subprocess, os

with open('reports-settings.yaml', "r", encoding='utf-8') as file:
    settings = yaml.safe_load(file)

os.chdir('scripts')

file_id = settings["file_id"]
pdf_name = f'{file_id}.pdf'
csv_name = f'{file_id}.csv'
json_name = f"{file_id}.json"
manufacturer = settings['manufacturer']
count = settings['count']
source_name = settings['source']['name']
source_url = settings['source']['url']

print('1. PDFからデータを抽出し、CSVファイルに保存します。')
print(f'{settings["name"]} のデータを "{pdf_name}" から抽出中\n', end='', flush=True)
subprocess.run([ "python", "./v2/extract-pdf-to-csv.py", pdf_name])
_ = input(f'./intermediate-files/{csv_name} の内容確認と修正が終わったら ENTER 押してください。')
print()

print('2. CSVデータを可能な限り整形し、どうしても手作業が残る箇所はログを出力します。')
print(f'{csv_name} のデータを整形中\n', end='', flush=True)
subprocess.run(["python", "./v2/standardize-csv.py", csv_name, manufacturer ])
_ = input(f'./intermediate-files/{csv_name} の内容確認と修正が終わったら ENTER 押してください。')
print()

print('3. CSVデータをJSONデータへと書き出します。')
print(f'手作業での修正が完了した {csv_name} に、最終的な整形を行ってJSONデータへと変換します。\n', end='', flush=True)
subprocess.run([ "python", "./v2/export-to-json.py", csv_name, count, json_name, source_name, source_url ])
print()