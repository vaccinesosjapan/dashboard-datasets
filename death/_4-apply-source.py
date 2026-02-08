import sys, re, json, unicodedata, os
import pandas as pd

json_file_name = sys.argv[1]
death_table_df = pd.read_csv('death-table.csv')
re_reports_file_name = re.compile(r'^(\d+)[\-\.]')

matched = re_reports_file_name.search(json_file_name)
if matched == None:
	print(f"[Error] JSONファイル名が条件に合致しません: {json_file_name}")
	exit(code=1)

matched_row_df = death_table_df[death_table_df['PDFファイル名'] == int(matched.group(1))].head(1).reset_index()

json_file_root_dir = "reports-data"
json_file_path = os.path.join(json_file_root_dir, json_file_name)
with open(json_file_path, "r", encoding='utf-8') as f:
	data = json.load(f)
	each_df = pd.DataFrame(data)

	source_array = [{ "name": matched_row_df.loc[0, '開催回'], "url": matched_row_df.loc[0, 'URL'] }] * each_df.shape[0]
	each_df['source'] = source_array
	ordinary_number = str(matched_row_df.loc[0, '開催回']).replace('第', '').replace('回', '')
	each_df['no'] = each_df['no'].astype(str)

	# ID文字列にワクチン名を使おうとしていたが、記号なども含まれていてややこしい文字列になるためJSONファイル名から
	# 拡張子を除去した「JSONファイル名」を用いて、「{検討部会の番号}-{JSONファイル名}-{該当する表でのNo}」とする。
	each_df['id'] = ordinary_number + '-' + json_file_name.replace(".json", "") + '-' + each_df['no']
	
	each_df['no'] = each_df['no'].astype(int)

	each_df_dict = each_df.to_dict("records")
	each_df_string = json.dumps(each_df_dict, ensure_ascii=False, indent=2)

with open(json_file_path, "w", encoding='utf-8') as f:
	f.write(each_df_string)