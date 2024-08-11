import sys, json, os, traceback, math, re
import pandas as pd

csv_file_name = sys.argv[1]
# 第2引数のpagesは、このスクリプトでは不要
vaccine_name = sys.argv[3]
source_dir = 'csv-summary-files'
output_dir = 'summary-data'

csv_file_path = os.path.join(source_dir, csv_file_name)
if not os.path.exists(csv_file_path):
	print(f'[エラー] csvファイル "{csv_file_path}" が見つかりません')
	sys.exit(1)
df = pd.read_csv(csv_file_path, delimiter=',')

try:
    numbers = {}
    row = df.loc[0]
    alpha = int(row['α'])
    beta = int(row['β'])
    gamma = int(row['γ'])
    numbers = { 
            "vaccine_name": vaccine_name,
            "evaluations": {
                "alpha": alpha,
                "beta": beta,
                "gamma": gamma
            }}

    if not bool(numbers):
        print('「因果関係評価結果」の読み取りに失敗しました！')
        sys.exit(1)
	
    json_string = json.dumps(numbers, ensure_ascii=False, indent=2)
    file_name = csv_file_name.rsplit('.', 1)[0]
    output_path = os.path.join(output_dir, file_name + '.json')
    with open( output_path, "w", encoding='utf-8') as f:
        f.write(json_string)

except Exception as e:
	print('Exception has occurred :-(')
	print("-"*60)
	print(f'name: {vaccine_name}')
	print(f'row: {row}', file=sys.stderr)
	traceback.print_exc(file=sys.stderr)
	print("-"*60)
	print()
	sys.exit(1)