from pathlib import Path
import pandas as pd
import os, sys, json
import yaml


def create_published_date_dataframe(df: pd.DataFrame) -> pd.DataFrame:
    '''
    第何回の検討部会がいつ開催されたのか（データが発表されたのか）という情報を記載した ordinal_number.yaml を読み込み
    医療機関からの副反応疑い報告一覧を使って「発表日」や「累計件数」をまとめたDataFrameを作る。
    '''
    with open("ordinal_number.yaml", encoding='utf-8') as f:
        data = yaml.safe_load(f)

    ordinal_numbers_dict = {}
    for item in data['ordinal_numbers']:
        ordinal_numbers_dict[item.get('name')] = item.get('date')
    
    df['ordinal_number'] = df['source'].map(lambda x: x['name'])
    df['published_date'] = df['ordinal_number'].map(lambda x: ordinal_numbers_dict[x])

    date_count_df = df.groupby('published_date', as_index=False)['no'].count().rename(columns={'no': 'count'})
    date_count_df = date_count_df.sort_values('published_date').reset_index(drop=True)
    date_count_df['cumulative_count'] = date_count_df['count'].cumsum()

    return date_count_df


def extract_df_from_csv(csv_name: str) -> pd.DataFrame:
    '''
    CSVから報告日と件数、累計件数の情報を抽出してDataFrame形式で返す。
    '''
    script_dir = Path.cwd()
    df = pd.read_csv(os.path.join(script_dir, "csv-files", csv_name))
    df['published_date'] = df['published_date'].str.replace('年','/').str.replace('月','/').str.replace('日','')
    df = df.drop(columns=['name','date_range', 'remarks']).rename(columns={"delta": "count"}).reindex(columns=['published_date','count','cumulative_count'])

    return df


def merge_and_sum_counts(left_df: pd.DataFrame, right_df: pd.DataFrame) -> pd.DataFrame:
    '''
    CSVから読み込んだ累計件数の情報をマージする処理。
    '''
    merged_df = pd.merge(left=left_df, right=right_df, on='published_date', how='left').fillna(0)
    merged_df['count'] = merged_df['count_x'] + merged_df['count_y']
    merged_df['cumulative_count'] = merged_df['cumulative_count_x'] + merged_df['cumulative_count_y']
    merged_df = merged_df.drop(columns=['count_x', 'count_y', 'cumulative_count_x', 'cumulative_count_y'])
    merged_df['count'] = merged_df['count'].astype(int)
    merged_df['cumulative_count'] = merged_df['cumulative_count'].astype(int)

    return merged_df


def save_json_from_dataframe(df: pd.DataFrame, json_file_path: str):
    '''
    DataFrameを直接JSON保存すると日付データなどが意図したようなフォーマットで保存されないため、それを解消して良い感じに保存する処理。
    '''
    df_dict = df.to_dict("records")
    df_string = json.dumps(df_dict, ensure_ascii=False, indent=2)

    with open(json_file_path, encoding='utf-8', mode='w', newline='\n') as f:
        f.write(df_string)


def main() -> int:
    root_dir = Path(__file__).parents[2]
    reports_file_path = os.path.join(root_dir, "_datasets", "medical-institution-reports.json")
    df = pd.read_json(reports_file_path)
    date_count_df = create_published_date_dataframe(df=df)

    p_df = extract_df_from_csv("pfizer.csv")
    a_df = extract_df_from_csv("astrazeneca.csv")
    m_df = extract_df_from_csv("moderna.csv")
    merged_df = merge_and_sum_counts(p_df, a_df)
    merged_df = merge_and_sum_counts(merged_df, m_df)

    date_count_df = date_count_df.drop(index=0)
    cat_df = pd.concat([merged_df, date_count_df])
    cat_df = cat_df.reset_index(drop=True)

    json_file_path = os.path.join(root_dir, "_datasets", "medical-institution-cumulative.json")
    save_json_from_dataframe(df=cat_df, json_file_path=json_file_path)

    return 0


if __name__ == "__main__":
    sys.exit(main())
