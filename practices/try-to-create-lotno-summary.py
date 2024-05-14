# ロットNoに「不明」が含まれているものや空白のものをinvalid_lotno_dfに保持し、
# それ以外のもの（集計対象）をvalid_lotno_dfに保持する。
# valid_dfのトップ10を抽出する。

import os,json
import pandas as pd

output_dir = '../_datasets'

json_file_path = os.path.join(output_dir, 'medical-institution-reports.json')
df = pd.read_json(json_file_path)

print(f'total count: {df.shape[0]}')

invalid_lotno_df = df[df['lot_no'].map(lambda x: str(x).__contains__('不明') or not str(x))]
#print(unknown_df)
invalid_count = invalid_lotno_df['no'].shape[0]
print(f'invalid lot_no count: {invalid_count}')

valid_lotno_df = df[df['lot_no'].map(lambda x: not str(x).__contains__('不明'))]
valid_count = valid_lotno_df['no'].shape[0]
print(f'valid lot_no count: {valid_count}')
print()

top_ten = valid_lotno_df.groupby(['lot_no'])['no'].count().nlargest(10)
print(top_ten)
print()

json_string = json.dumps(top_ten.to_dict(), ensure_ascii=False, indent=2)
print(json_string)
print()