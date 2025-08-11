# %%
import pandas as pd
import json, os

source_dir = '../_datasets'
output_dir = '../_datasets'

# %%
source_path = os.path.join(source_dir, 'certified-reports.json')
df = pd.read_json(source_path)
pivot_df = df.pivot_table('no', index=['certified_date'], columns=['description_of_claim', 'judgment_result'], aggfunc='count', observed=False).fillna(0).astype(int)

# %%
# 亡くなった方々に関する請求内容がいくつか分かれてしまっているので「死亡一時金', '葬祭料」として合算してまとめる。
pivot_df[('merged', '認定')] = pivot_df[('死亡一時金', '認定')] + pivot_df[('葬祭料', '認定')] + pivot_df[('死亡一時金・葬祭料', '認定')]
pivot_df[('merged', '否認')] = pivot_df[('死亡一時金', '否認')] + pivot_df[('葬祭料', '否認')] + pivot_df[('死亡一時金・葬祭料', '否認')]
pivot_df.drop(columns=[
	('死亡一時金', '否認'), ('死亡一時金', '認定'),
	('死亡一時金・葬祭料', '否認'), ('死亡一時金・葬祭料', '認定'),
	('葬祭料', '否認'), ('葬祭料', '認定')
], inplace=True)
pivot_df.rename(columns={'merged': '死亡一時金・葬祭料'}, inplace=True)

# %%
# 列名を半角英数の文字列に変換しつつ、MultiIndexを解除してフラットな文字列に。
columns_replace_dict = {
	'医療費・医療手当': 'medical',
	'死亡一時金・葬祭料': 'death',
	'障害児養育年金': 'disability_of_children',
	'障害年金': 'disability',
	'認定': 'certified',
	'否認': 'denied'
}
pivot_df.rename(columns=columns_replace_dict, inplace=True)
pivot_df.columns = ['_'.join(col) for col in pivot_df.columns]

# %%
# 列の順番を整える。
pivot_df = pivot_df.reindex(columns=[
	'medical_certified', 'medical_denied',
	'death_certified', 'death_denied',
	'disability_of_children_certified', 'disability_of_children_denied',
	'disability_certified', 'disability_denied',
])

# %%
# 累計データの作成
for col in pivot_df.columns:
	pivot_df[f'{col}_sum'] = pivot_df[col].cumsum()

# %%
# 列名から、グラフ側で表示する名称を得るための辞書を作る。
display_name_base_dict = {
	'medical_certified': "認定件数（医療費・医療手当）",
	'medical_denied': '否認件数（医療費・医療手当）',
	'death_certified': '認定件数（死亡一時金・葬祭料）',
	'death_denied': '否認件数（死亡一時金・葬祭料）',
	'disability_of_children_certified': '認定件数（障害児養育年金）',
	'disability_of_children_denied': '否認件数（障害児養育年金）',
	'disability_certified': '認定件数（障害年金）',
	'disability_denied': '否認件数（障害年金）',
}
display_name_dict = dict()
for k, v in display_name_base_dict.items():
	display_name_dict[k] = v
	display_name_dict[f'{k}_sum'] = v

# %%
data_list = []
for col in pivot_df.columns:
    data = {
        "id": pivot_df[col].name,
        "display_name": display_name_dict[pivot_df[col].name],
        "certified": col.__contains__('certified'),
        "cumulative": col.endswith('_sum'),
        "y_axis_data": pivot_df[col].tolist()
	}
    data_list.append(data)

data_for_frontend = {
    "x_axis_data": pivot_df.index.to_list(),
	"data_list": data_list,
}

output_path = os.path.join(output_dir, 'judged-split-data.json')
with open(output_path, 'w', encoding='utf-8') as f:
    json.dump(data_for_frontend, f, ensure_ascii=False, separators=(',', ':'))


