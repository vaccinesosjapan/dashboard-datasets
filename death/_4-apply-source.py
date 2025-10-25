import sys, re, json, unicodedata
import pandas as pd

json_path = sys.argv[1]
death_table_df = pd.read_csv('death-table.csv')
re_reports_file_name = re.compile(r'^(\d+)[\-\.]')

matched = re_reports_file_name.search(json_path.replace('.\\reports-data\\', ''))
matched_row_df = death_table_df[death_table_df['PDFファイル名'] == int(matched.group(1))].head(1).reset_index()

with open(json_path, "r", encoding='utf-8') as f:
	data = json.load(f)
	each_df = pd.DataFrame(data)

	source_array = [{ "name": matched_row_df.loc[0, '開催回'], "url": matched_row_df.loc[0, 'URL'] }] * each_df.shape[0]
	each_df['source'] = source_array
	ordinary_number = matched_row_df.loc[0, '開催回'].replace('第', '').replace('回', '')
	each_df['no'] = each_df['no'].astype(str)
	each_df['id'] = ordinary_number + '-' + unicodedata.normalize("NFKC", matched_row_df.loc[0, 'ワクチン名']) + '-' + each_df['no']
	each_df['no'] = each_df['no'].astype(int)

	each_df_dict = each_df.to_dict("records")
	each_df_string = json.dumps(each_df_dict, ensure_ascii=False, indent=2)

with open(json_path, "w", encoding='utf-8') as f:
	f.write(each_df_string)