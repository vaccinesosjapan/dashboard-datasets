import os, sys, typing, re
import pandas as pd
import camelot


def remove_empty_lines(source_path, target_path):
    '''
    DataFrameのto_csv処理では今後の処理で不要な内容が含まれるため、これを削除する。
    '''
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

    with open(target_path, "w", encoding="utf-8", newline='\n') as f:
        f.write(fixed_data)


def main():
    pdf_dir_path = os.path.join('..', 'pdf-files')
    csv_dir_path = os.path.join('..', 'intermediate-files')

    file_id = sys.argv[1] # '001694121-myocarditis'
    pages = sys.argv[2] # '3'
    pdf_file_name = f"{file_id.split('-')[0]}.pdf" # '001694121.pdf'
    csv_file_name = f"{file_id}.csv" # ''001694121-myocarditis.csv'

    pdf_file_path = os.path.join(pdf_dir_path, pdf_file_name)
    tables = camelot.read_pdf(pdf_file_path, pages=pages)
    print(f"抽出したtable数: {len(tables)}")

    merged_df = pd.DataFrame()
    for index, table in enumerate(tables):
        if index == 0:
            merged_df = typing.cast(pd.DataFrame, table.df)
        else:
            df = typing.cast(pd.DataFrame, table.df)
            merged_df = pd.merge(merged_df, df, how='outer')
    print(f'マージしたDataFrameの行数: {merged_df.shape[0]}')

    csv_data = merged_df.to_csv(index=False)
    
    csv_file_path = os.path.join(csv_dir_path, csv_file_name)
    with open(csv_file_path, "w", encoding='utf-8', newline='\n') as f:
        f.write(csv_data)
    
    remove_empty_lines(csv_file_path, csv_file_path)
    print(f'{csv_file_path} に抽出結果を保存しました。')


if __name__ == '__main__':
    main()