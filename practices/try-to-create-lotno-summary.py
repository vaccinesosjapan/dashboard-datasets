# ロットNoに「不明」が含まれているものをunknown_dfに保持し、
# 含まれていないもの（集計対象）をvalid_dfに保持する。
# valid_dfのトップ10を抽出する。

import os,json
import pandas as pd

output_dir = '../_datasets'

json_file_path = os.path.join(output_dir, 'medical-institution-reports.json')
df = pd.read_json(json_file_path)

unknown_df = df[df['lot_no'].map(lambda x: str(x).__contains__('不明'))]
#print(unknown_df)
unknown_df_count = unknown_df['no'].shape[0]
print(f'unknown lot_no count: {unknown_df_count}')
print()

valid_df = df[df['lot_no'].map(lambda x: not str(x).__contains__('不明'))]
top_ten = valid_df.groupby(['lot_no'])['no'].count().nlargest(10)
print(top_ten)
print()

json_string = json.dumps(top_ten.to_dict(), ensure_ascii=False, indent=2)
print(json_string)
print()