import os, re, sys
import pandas as pd


def split_age_and_gender(df: pd.DataFrame) -> None:
    '''
    中点「・」で区切って記載されている年齢と性別を分離して別々の列にする。
    引数で受け取ったDataFrameを直接編集する点に注意。
    '''
    age_and_gender_df = df['age_and_gender'].str.split('・', expand=True)
    if len(age_and_gender_df.columns) == 2:
        age_and_gender_df.columns = ['age', 'gender']
        df.insert(1, "age", age_and_gender_df['age'])
        df.insert(2, "gender", age_and_gender_df['gender'])
        df = df.drop('age_and_gender', axis=1)
    else:
        print(" - 年齢と性別の分離ができませんでした。データを確認してください。")


def split_vaccine_name_and_lot_no(df: pd.DataFrame) -> None:
    '''
    ワクチン名とロット番号が同じセルに記載されているため、これを分離して別々の列にする。
    引数で受け取ったDataFrameを直接編集する点に注意。
    '''
    # 全角のかっこ（）に囲まれたロット番号だけを抽出して別の列にする
    regex = re.compile('(?<=（).+?(?=\）)')
    lot_no_series = df['vaccine_name'].map(lambda x: regex.findall(str(x).replace('\r\n', '\n').replace('\n', ''))[0])
    df['lot_no'] = lot_no_series

    # ワクチン名だけにする
    df['vaccine_name'] = df['vaccine_name'].map(lambda x: str(x).replace('\r\n','\n').replace('\n','').split('（')[0])


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

        with open(target_path, "w", encoding="utf-8", newline='\n') as f:
            f.write(fixed_data)


def main():
    csv_folder = 'intermediate-files'
    csv_name = sys.argv[1]
    manufacturer = sys.argv[2]

    csv_path = os.path.join('..', csv_folder, csv_name)
    df = pd.read_csv(csv_path, encoding='utf-8')

    # 冒頭の「期間」と「評価」列は不要なため削除
    df = df.drop(columns=df.columns[[0, 1]])
    df.columns = ['no', 'vaccine_name', 'age_and_gender', 'pre_existing_disease_names', 'keika', 'PT_names', 'gross_results', 'brighton_classification', 'evaluated_result', 'expert_opinion']

    split_age_and_gender(df)
    split_vaccine_name_and_lot_no(df)

    # 不足している列を追加
    df['vaccinated_date'] = ''
    df['onset_dates'] = ''
    df['days_to_onset'] = ''
    df['gross_result_dates'] = ''
    df['evaluated_PT'] = ''
    df['manufacturer'] = manufacturer
    df['vaccinated_times'] = ''
    df['remarks'] = ''

    # 不要な列を削除
    df = df.drop('keika', axis=1)

    # 列の並び替え
    new_columns = ['no', 'age', 'gender', 'vaccinated_date', 'onset_dates', 'days_to_onset', 'vaccine_name', 'manufacturer', 'vaccinated_times', 'lot_no', 'pre_existing_disease_names', 'PT_names', 'gross_result_dates', 'gross_results', 'evaluated_PT', 'evaluated_result', 'brighton_classification', 'expert_opinion', 'remarks']
    df = df.reindex(columns=new_columns)

    with open(csv_path, encoding='utf-8', mode='w', newline='\n') as f:
        f.write(df.to_csv(index=False))

    remove_empty_lines(csv_path, csv_path)
    print(f'{csv_path} に正規化した結果を保存しました。')


if __name__ == '__main__':
    main()