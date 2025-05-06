# %%
import os, json
from collections import defaultdict
import numpy as np
import pandas as pd
from natsort import index_natsorted

json_file_path = os.path.join('..', '_datasets', 'medical-institution-reports.json')
df = pd.read_json(json_file_path)

# %%
# 過去データでは concurrent_vaccination_flag が NaN になる箇所がある。これらをbool型のfalseに変換する。
concurrent_vaccination_flag_isna_df = df[df['concurrent_vaccination_flag'].isna()]
df.loc[concurrent_vaccination_flag_isna_df.index, 'concurrent_vaccination_flag'] = 0.0
df['concurrent_vaccination_flag'] = df['concurrent_vaccination_flag'].astype(bool)

df.loc[concurrent_vaccination_flag_isna_df.index, 'concurrent_vaccination'] = ''

# %%
concurrent_vaccination_df = df[df['concurrent_vaccination_flag']]
cv_unique = concurrent_vaccination_df['concurrent_vaccination'].unique()
if cv_unique.__contains__(''):
	print(f'[Warn] 同時接種のフラグがTrueなのに、同時接種情報が空のものがありそうです。: {cv_unique}')

# %%
non_concurrent_vaccination_df = df[~df['concurrent_vaccination_flag']]
non_cv_unique = non_concurrent_vaccination_df['concurrent_vaccination'].unique()
if len(non_cv_unique) > 1:
	print(f'[Warn] 同時接種のフラグがFalseなのに、同時接種情報が空で無いものがありそうです。: {non_cv_unique}')

# %%
# 2025年よりも前のデータには含まれていない列も多いため、NaNの箇所が多数ある。これらを空白文字列に置換しておく。
df = df.fillna('')

# id 列を先頭にする
df = df[['id'] + [col for col in df.columns if col not in ['id']]]

# %%
# original source: https://qiita.com/Lisphilar/items/b5d0a4e8ecb77f9c51f6
def int2ordinal(num: int):
    """
    Convert a natural number to a ordinal number.
        Args:
            num (int): natural number
        Returns:
            str: ordinal number, like 0th, 1st, 2nd,...
        Notes:
            Zero can be used as @num argument.
    """
    if not isinstance(num, int):
        raise TypeError(
            f"@num must be integer, but {num} was applied.")
    if num < 0:
        raise ValueError(
            f"@num must be over 0, but {num} was applied.")
    ordinal_dict = defaultdict(lambda: "th")
    ordinal_dict.update({1: "st", 2: "nd", 3: "rd"})
    q, mod = divmod(num, 10)
    suffix = "th" if q % 10 == 1 else ordinal_dict[mod]
    return f"{num}{suffix}"

# %%
# source 列のデータから第何回のデータなのか、という情報を抽出してID文字列を生成
id_nan_df = df[df['id'] == '']
if len(id_nan_df) != 0:
	source_name_series = id_nan_df['source'].apply(pd.Series)
	source_name_series['prefix-number'] = source_name_series['name'].str.replace('第', '').str.replace('回', '')
	source_name_series['prefix-number'] = source_name_series['prefix-number'].astype(int)
	source_name_series['prefix'] = source_name_series['prefix-number'].map(lambda x: int2ordinal(x))

    # 2025年以降のデータでは、医療機関（Medical institution）からの報告のうち、重い（Serious）な症例と
    # それ以外（Not serious）を識別する必要があり、それぞれ MIS と MIN という識別子を適用する。
	source_name_series['kind'] = id_nan_df['severity'].map(lambda x: 'MIS' if x == '重い' else 'MIN')
	source_name_series['no'] = id_nan_df['no'].astype(str)

	source_name_series['id'] = source_name_series['prefix'] + '-' + source_name_series['kind'] + '-' + source_name_series['no']

	df.loc[id_nan_df.index, 'id'] = source_name_series['id']

# %%
# IDでいい感じにソートする
df = df.sort_values(
    by="id",
    key=lambda x: np.argsort(index_natsorted(df["id"]))
)

# %%
# 日付のスラッシュがエスケープされないようにするため、json.dumpsを使って文字列化する
df_dict = df.to_dict("records")
df_string = json.dumps(df_dict, ensure_ascii=False, indent=2)

with open(json_file_path, encoding='utf-8', mode='w') as f:
	f.write(df_string)


