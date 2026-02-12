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

	# ID文字列のフォーマットは「{検討部会の番号}-{ワクチン名}-{該当する表でのNo}」とする。
	vaccine_name = ""
	for v_name in each_df.iloc[:, 2]:
		vaccine_name = unicodedata.normalize("NFKC", str(v_name))
		if "\n" in vaccine_name:
			# 複数のワクチンが書かれているエントリーは使用したくないため、別の候補を探す。
			continue
	each_df['id'] = ordinary_number + '-' + vaccine_name + '-' + each_df['no']
	
	each_df['no'] = each_df['no'].astype(int)

	each_df_dict = each_df.to_dict("records")
	each_df_string = json.dumps(each_df_dict, ensure_ascii=False, indent=2)

with open(json_file_path, "w", encoding='utf-8') as f:
	f.write(each_df_string)