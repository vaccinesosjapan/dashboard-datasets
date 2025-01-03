# %%
import os, sys, unicodedata, json, math, glob
import yaml
import pandas as pd

# スクリプトをエクスポートするパスに応じて、ここのパス設定を調整してください。
csv_file_path = os.path.join('expected-issues.csv')
json_file_path = os.path.join('..', '_datasets', 'carditis-reports.json')
metadata_file_path = os.path.join('metadata.yaml')
reports_dir_path = os.path.join('reports-data')
output_path = os.path.join('..', '_datasets', 'carditis-summary.json')

df = pd.read_csv(csv_file_path, encoding='utf8')

# %%
myocarditis_df = df[df['carditis_types'] == 'myocarditis']
pericarditis_df = df[df['carditis_types'] == 'pericarditis']

if df.shape[0] != myocarditis_df.shape[0] + pericarditis_df.shape[0]:
	print(f'Error: 心筋炎と心膜炎以外のcarditis_typesが設定されているようです。expected-issues.csvの確認をお願いします。')
	sys.Exit(1)

mDf_by_manufacturer = myocarditis_df.groupby('manufacturer', as_index=False)['count'].sum().sort_values('count', ascending=False)
pDf_by_manufacturer = pericarditis_df.groupby('manufacturer', as_index=False)['count'].sum().sort_values('count', ascending=False)

# %%
myocarditis_sum_count = int(mDf_by_manufacturer['count'].sum())
pericarditis_sum_count = int(pDf_by_manufacturer['count'].sum())
total_sum_count = myocarditis_sum_count + pericarditis_sum_count

# %%
df_m = myocarditis_df.rename(columns={'count': 'myocarditis_count'}).drop(['carditis_types'], axis=1)
df_p = pericarditis_df.rename(columns={'count': 'pericarditis_count'}).drop(['carditis_types'], axis=1)
merged_df = pd.merge(df_m, df_p, on=['file_name_prefix', 'manufacturer', 'name'])

# %%
merged_df['name'] = merged_df['name'].map(lambda x: unicodedata.normalize("NFKC", str(x)))
merged_df = merged_df.drop(['file_name_prefix', 'manufacturer'], axis=1)
df_by_vaccine_name = merged_df.rename(columns={'name': 'vaccine_name'})

# %%
# 集計した症例一覧のデータを読み込み、情報の抽出や「予測値」とのチェック、特定列の値のチェックなどを行う。
with open(json_file_path, 'r', encoding='utf-8') as f:
    data = json.load(f)
reports_df = pd.json_normalize(data)

# %%
empty_manufacturer_df = reports_df[reports_df['manufacturer'] == '']
if empty_manufacturer_df.shape[0] != 0:
	print('製造販売業者が空のデータがあります:\n')
	for label, value in empty_manufacturer_df.items():
		if label == 'no':
			print(f' - {value.index}')
	print()

# %%
m_reports_path = os.path.join(reports_dir_path, '*-myocarditis.json')
m_reports_path_list = glob.glob(m_reports_path)
m_data_list = []
for m_path in m_reports_path_list:
	with open(m_path, 'r', encoding='utf-8') as f:
		m_data_list.extend(json.load(f))
m_reports_df = pd.DataFrame(m_data_list)
if myocarditis_sum_count != m_reports_df.shape[0]:
	print('心筋炎の件数が予測件数と異なります\n')
	print(f' - 予測件数: {myocarditis_sum_count} [件]\n - 抽出した症例件数: {m_reports_df.shape[0]} [件]\n')
	print(m_reports_df.groupby('vaccine_name')['no'].count())
	print()

# %%
p_reports_path = os.path.join(reports_dir_path, '*-pericarditis.json')
p_reports_path_list = glob.glob(p_reports_path)
p_data_list = []
for p_path in p_reports_path_list:
	with open(p_path, 'r', encoding='utf-8') as f:
		p_data_list.extend(json.load(f))
p_reports_df = pd.DataFrame(p_data_list)
if pericarditis_sum_count != p_reports_df.shape[0]:
	print('心膜炎の件数が予測件数と異なります\n')
	print(f' - 予測件数: {pericarditis_sum_count} [件]\n - 抽出した症例件数: {p_reports_df.shape[0]} [件]\n')
	print(p_reports_df.groupby('vaccine_name')['no'].count())
	print()

# %%
def sum_carditis_by_ages(df):
    df['age'] = df['age'].map(lambda x: str(x).replace('歳代','').replace('歳','').replace('代',''))
    df = df[["age"]]
    
    unknown_ages_count = df[~df['age'].str.isdecimal()].shape[0]

    df = df[df['age'].str.isdecimal()]
    df['age'] = df['age'].astype(int)
    ages_count = df.shape[0]
    
    df['generation'] = df['age'].apply(lambda x:math.floor(x/10)*10)
    df['count'] = 1
    df = df.drop(columns=['age'])
    
    aged_df = df.groupby('generation').sum()
    aged_df = aged_df.reset_index()
    aged_df['generation'] = aged_df['generation'].map(lambda x: str(x) + '代')
    aged_df = aged_df.rename(columns={'generation': 'x'})
    aged_df = aged_df.rename(columns={'count': 'y'})
    aged_df.to_dict(orient='records')

    return (aged_df, unknown_ages_count, ages_count)


(aged_df, unknown_ages_count, ages_count) = sum_carditis_by_ages(reports_df)

# %%
with open(metadata_file_path, "r", encoding='utf-8') as f:
    metadata_root = yaml.safe_load(f) 
metadata = metadata_root['metadata']

# %%
summary_data = {
	"carditis_summary": {
		"date": metadata['commission_of_inquiry_date'],
		"total": total_sum_count,
		"myocarditis": myocarditis_sum_count,
		"pericarditis": pericarditis_sum_count,
		"source": metadata['source'],
	},
	"carditis_issues": {
        "date": metadata['data_end_date'],
		"issues_with_vaccine_name": df_by_vaccine_name.to_dict(orient='records'),
        "issues_m_by_manufacturers": mDf_by_manufacturer.to_dict(orient='records'),
        "issues_p_by_manufacturers": pDf_by_manufacturer.to_dict(orient='records'),
        "issues_by_ages": {
            "ages_count": ages_count,
            "unknown_ages_count": unknown_ages_count,
            "issues": aged_df.to_dict(orient='records')
        }
	}
}

# %%
json_string = json.dumps(summary_data, ensure_ascii=False, indent=2)
with open( output_path, "w", encoding='utf-8') as f:
    f.write(json_string)


