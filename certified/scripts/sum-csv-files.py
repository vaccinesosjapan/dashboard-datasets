# %%
import pandas as pd
import glob, os, re

csv_file_list = glob.glob('intermediate-files/*.csv')

merged_df = pd.DataFrame()
for file in csv_file_list:
	with open(file, "r", encoding='utf-8') as f:
		# 「否認理由」列が浮動小数点として読み取られると3.0みたいになってしまうため、一律に文字列として読み取る。
		df = pd.read_csv(f, dtype={'否認理由': str})
		if merged_df.empty:
			merged_df = df
		else:
			merged_df = pd.concat([merged_df, df], ignore_index=True)

# %%
# 年の為にJSONも読み込んで確認する用。CSVの方は判定が「保留」のデータも含んでいる点に注意。
'''
json_file_list = glob.glob('../reports-data/*.json')

merged_df2 = pd.DataFrame()
for file in json_file_list:
	with open(file, "r", encoding='utf-8') as f:
		df = pd.read_json(f)
		if merged_df2.empty:
			merged_df2 = df
		else:
			merged_df2 = pd.concat([merged_df2, df], ignore_index=True)
'''

# %%
def remove_empty_lines(source_path, target_path):
    fixed_data = ''
    with open(source_path, encoding="utf-8-sig") as f:
        for line in f:
            if not line.isspace():
                if line.startswith(','):
                    line = re.sub('^,', '', line)
                fixed_data += line

    with open(target_path, "w", encoding="utf-8-sig") as f:
        f.write(fixed_data)

# %%
output_path = os.path.join('..', '_datasets', 'reference-data', 'certified-reports.csv')
with open(output_path, "w", encoding='utf-8-sig') as f:
	merged_df.to_csv(f, encoding='utf-8-sig', index=False)

remove_empty_lines(output_path, output_path)
