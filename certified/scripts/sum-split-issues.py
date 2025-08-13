# %%
import pandas as pd
import json, os, copy

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
columns_dict = {
	'医療費・医療手当': 'medical',
	'死亡一時金・葬祭料': 'death',
	'障害児養育年金': 'disability_of_children',
	'障害年金': 'disability'
}
columns_replace_dict = copy.deepcopy(columns_dict)
columns_replace_dict['認定'] = 'certified'
columns_replace_dict['否認'] = 'denied'

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
# グラフ側で表示する名称を得るための辞書を作る。
display_name_dict = dict()
for k, v in columns_dict.items():
	display_name_dict[v] = k

# %%
def get_margin(data: int) -> int:
	if 0 < data and data < 50:
		return 5
	elif 50 <= data and data < 100:
		return 10
	elif 100 <= data and data < 1000:
		return 50
	elif 1000 <= data and data < 5000:
		return 100
	elif 5000 <= data and data < 10000:
		return 500
	else:
		return 1000

def get_round_param(data: int) -> int:
	if 0 < data and data < 100:
		return -1
	elif 100 <= data and data < 1000:
		return -1
	elif 1000 <= data and data < 10000:
		return -2
	else:
		return -3

def get_fine_rounded_value(max_val: int) -> int:
	margin = get_margin(max_val)
	param = get_round_param(max_val)
	return int(round(max_val + margin, param))

# %%
data_list = []
for k, v in display_name_dict.items():
    # グラフ側でY軸の値をどのぐらいにすればよいかを示す値を計算してデータに含める。
    max_data = (pivot_df[f'{k}_certified'] + pivot_df[f'{k}_denied']).max()
    normal_y_axis_max = get_fine_rounded_value(max_data)

    last_sum_data = pivot_df[f'{k}_certified_sum'].iloc[-1] + pivot_df[f'{k}_denied_sum'].iloc[-1]
    sum_y_axis_max = get_fine_rounded_value(last_sum_data)

    '''
    # debug print
    print(k)
    print(f'normal: max={max_data}, axis_max={normal_y_axis_max}')
    print(f'sum   : max={last_sum_data}, axis_max={sum_y_axis_max}')
    print()
    '''

	# NaNをnullに変換しておけば、JSON出力した際にもフロントエンドで解釈可能なnullとして出力される。
    # 最初はfillna(0)でゼロ埋めしようと思ったのだが、認定比率のグラフ的に微妙だったのでやめた。
    data = {
			"id": k,
			"display_name": v,
			"certified_data": pivot_df[f'{k}_certified'].tolist(),
			"certified_sum_data": pivot_df[f'{k}_certified_sum'].tolist(),
			"denied_data": pivot_df[f'{k}_denied'].tolist(),
			"denied_sum_data": pivot_df[f'{k}_denied_sum'].tolist(),
			"certified_rate": round(pivot_df[f'{k}_certified'] / (pivot_df[f'{k}_certified'] + pivot_df[f'{k}_denied']) * 100, 2).fillna(0).tolist(),
            "certified_rate_sum": round(pivot_df[f'{k}_certified_sum'] / (pivot_df[f'{k}_certified_sum'] + pivot_df[f'{k}_denied_sum']) * 100, 2).fillna(0).tolist(),
            "normal_y_axis_max": normal_y_axis_max,
            "sum_y_axis_max": sum_y_axis_max,
		}
    data_list.append(data)

data_for_frontend = {
    "x_axis_data": pivot_df.index.to_list(),
	"data_list": data_list
}

output_path = os.path.join(output_dir, 'judged-split-data.json')
with open(output_path, 'w', encoding='utf-8') as f:
    json.dump(data_for_frontend, f, ensure_ascii=False, separators=(',', ':'))


