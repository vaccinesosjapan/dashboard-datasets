import os, sys, typing, re
import pandas as pd
import camelot

pdf_file_name = sys.argv[1] # '001325489.pdf'
pages = sys.argv[2] # '30-45'
symptoms = sys.argv[3] # 'myocarditis'

pdf_file_path = os.path.join('..', 'pdf-files', pdf_file_name)
tables = camelot.read_pdf(pdf_file_path, pages=pages, encoding='utf-8')

print(f"症状: {symptoms}")
print(f"抽出したtable数 {len(tables)}")

merged_df = pd.DataFrame()
for index, table in enumerate(tables):
	if index == 0:
		merged_df = typing.cast(pd.DataFrame, table.df)
	else:
		df = typing.cast(pd.DataFrame, table.df)
		merged_df = pd.merge(merged_df, df, how='outer')

csv_data = merged_df.to_csv(index=False)

pdf_file_name_without_ext = os.path.splitext(pdf_file_name)[0]
csv_file_path = os.path.join('..', 'intermediate-files', f'{pdf_file_name_without_ext}-{symptoms}.csv')
with open(csv_file_path, "w", encoding='utf-8') as f:
	f.write(csv_data)

print(f'マージしたDataFrameの行数: {merged_df.shape[0]}')

def remove_empty_lines(source_path, target_path):
    fixed_data = ''
    with open(source_path, encoding="utf-8") as f:
        for line in f:
            if not line.isspace():
                if line.startswith(','):
                    line = re.sub('^,', '', line)
                fixed_data += line

    with open(target_path, "w", encoding="utf-8") as f:
        f.write(fixed_data)

remove_empty_lines(csv_file_path, csv_file_path)

print(f'{csv_file_path} に抽出結果を保存しました。')

# %% [markdown]
# PDFからデータを抽出して、Excelなどを使ってテーブル形式で見ながら列が変な箇所を修正できるようにする。
# 一度の抽出で、400件弱でも6分半かかったりするので、抽出工程の頻度を極力減らした方が良い。
# 結構形がごちゃごちゃで規則性があまり無いため、目視で見ながらテーブルを修正するのが最善だと感じた。
# データを改行でセル分割する場合は、`その他`で「Ctrl + j」を入力すると良いみたい。
