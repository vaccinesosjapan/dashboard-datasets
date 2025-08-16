# %%
import pandas as pd
import os, sys
from io import StringIO

file_id = sys.argv[1]
json_path = os.path.join('reports-data', f'{file_id}.json')

with open(json_path, 'r', encoding='utf-8') as jf:
    df = pd.read_json(jf)

# %%
df.drop(["certified_date", "source_url"], axis=1, inplace=True)

# %%
df = df.reindex(columns=['gender', 'age', 'vaccine_name', 'description_of_claim', 'symptoms', 'pre_existing_conditions', 'judgment_result', 'reasons_for_repudiation', 'remarks'])
df.rename(columns={'gender': '性別', 'age': '年齢', 'vaccine_name': 'ワクチン名', 'description_of_claim': '請求内容',
				   'symptoms': '疾病名', 'pre_existing_conditions': '基礎疾患', 'judgment_result': '判定',
				   'reasons_for_repudiation': '否認理由', 'remarks': '備考'}, inplace=True)

# %%
# 否認理由のTypeA-やTypeB-で始まる情報を、末尾の数字文字列だけの配列に変換する。
def convert_reasons_type_to_numbers(lst):
    if not isinstance(lst, list) or len(lst) == 0:
        return ''
    return ','.join([ typeStr.replace('TypeA-', '').replace('TypeB-', '') for typeStr in lst])

# %%
# 数値の配列を文字列の配列に変換しつつ「歳」を付与して、複数ある場合は読点でつなぐ。
df['年齢'] = df['年齢'].apply(lambda x: '、'.join([f"{num}歳" for num in x]))
df['疾病名'] = df['疾病名'].apply(lambda x: '、'.join(x))
df['基礎疾患'] = df['基礎疾患'].apply(lambda x: '、'.join(x))
df['否認理由'] = df['否認理由'].apply(convert_reasons_type_to_numbers)

# %%
csv_path = os.path.join('intermediate-files', f'{file_id}.csv')
df.to_csv(csv_path, index=False)


