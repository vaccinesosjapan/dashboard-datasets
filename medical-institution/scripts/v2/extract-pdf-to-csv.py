# %%
import os, typing, re, sys
import pandas as pd
import camelot

# スクリプトへとエクスポートした際に調整が必要な各種パス情報
relative_dir = sys.argv[1]
pdf_dir_path = os.path.join('..', 'pdf-files', relative_dir)
csv_dir_path = os.path.join('..', 'intermediate-files', relative_dir)
pdf_file_name = sys.argv[2]
csv_file_name = sys.argv[3]
pages = sys.argv[4]

# %%
pdf_file_path = os.path.join(pdf_dir_path, pdf_file_name)
tables = camelot.read_pdf(pdf_file_path, pages=pages)

print(f"抽出したtable数: {len(tables)}")

# %%
merged_df = pd.DataFrame()
for index, table in enumerate(tables):
	if index == 0:
		merged_df = typing.cast(pd.DataFrame, table.df)
	else:
		df = typing.cast(pd.DataFrame, table.df)
		merged_df = pd.merge(merged_df, df, how='outer')

csv_data = merged_df.to_csv(index=False)

# %%
csv_file_path = os.path.join(csv_dir_path, csv_file_name)
with open(csv_file_path, "w", encoding='utf-8') as f:
	f.write(csv_data)

# %%
print(f'マージしたDataFrameの行数: {merged_df.shape[0]}')

# %%
def remove_empty_lines(source_path, target_path):
    fixed_data = ''
    with open(source_path, encoding="utf-8") as f:
        for line in f:
            if line.isspace():
                continue
            if line.startswith('0,1,2,3,4,5'):
                continue
            if line.startswith(','):
                line = re.sub('^,', '', line)
            fixed_data += line

    with open(target_path, "w", encoding="utf-8") as f:
        f.write(fixed_data)

remove_empty_lines(csv_file_path, csv_file_path)

# %%
print(f'{csv_file_path} に抽出結果を保存しました。')


