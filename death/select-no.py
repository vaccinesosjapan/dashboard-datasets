import sys, os
import pandas as pd

filter_strings = ['\n', '注', '※', '→']

file_name = sys.argv[1]
df = pd.read_json(os.path.join('extracted-data', file_name))

#print(df[df['no'].str.contains('|'.join(filter_strings))])
#print()

number_index_list = df['no'].astype(str).str.isdecimal()
number_df = df[number_index_list]
number_df = number_df.astype({'no': 'int32'})
not_number_index_list = list(map(lambda x: not x, number_index_list))
not_number_df = df[not_number_index_list]

#print(df[number_index_list].to_json(orient='records' ,force_ascii=False, indent=2))
#print()
#print(df[not_number_index_list].to_json(orient='records' ,force_ascii=False, indent=2))

if not number_df.empty:
    json_string = number_df.to_json(orient='records' ,force_ascii=False, indent=2)
    output_path = os.path.join('reports-data', file_name)
    with open( output_path, "w", encoding='utf-8') as f:
        f.write(json_string)

if not not_number_df.empty:
    json_string = not_number_df.to_json(orient='records' ,force_ascii=False, indent=2)
    output_path = os.path.join('intermediate-files', file_name)
    with open( output_path, "w", encoding='utf-8') as f:
        f.write(json_string)