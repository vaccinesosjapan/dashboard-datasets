import os, json
import pandas as pd

output_dir = '../_datasets'

source_dir = '../_datasets'
source_path = os.path.join(source_dir, 'certified-reports.json')
with open(source_path, "r", encoding='utf-8') as f:
	certified_reports = json.load(f)

date_list = []
certified_list = []
repudiation_list = []

for issue in certified_reports:
    date_list.append(issue['certified_date'])
    if issue['judgment_result'] == '認定':
        certified_list.append(1)
        repudiation_list.append(0)
    else:
        certified_list.append(0)
        repudiation_list.append(1)

df_0 = pd.DataFrame({'Date': date_list, 'CertifiedCount': certified_list, 'RepudiationCount': repudiation_list})
df = df_0.groupby('Date').agg(sum)
df['CertifiedRate'] = round(df['CertifiedCount'] / (df['CertifiedCount'] + df['RepudiationCount']) * 100, 2)
df['CertifiedCountSum'] = df['CertifiedCount'].cumsum()
df['RepudiationCountSum'] = df['RepudiationCount'].cumsum()
df['CertifiedRateSum'] = round( df['CertifiedCountSum'] / (df['CertifiedCountSum'] + df['RepudiationCountSum']) * 100, 2 )

unique_date_set = sorted(set(date_list))

# dataframeに対してgroupbyを実行すると、locなどで使う行のindexがgroupbyで指定したkeyになるようだ。
# そのことに気づけず少し時間を消費してしまったので、ここにメモを残す。
data_list = []
for rowIndex in unique_date_set:
	row = df.loc[rowIndex]
	data_list.append({
		'Date': rowIndex,
		'CertifiedCount': int(row['CertifiedCount'].item()),
		'RepudiationCount': int(row['RepudiationCount'].item()),
		'CertifiedRate': row['CertifiedRate'],
		'CertifiedCountSum': int(row['CertifiedCountSum'].item()),
		'RepudiationCountSum': int(row['RepudiationCountSum'].item()),
		'CertifiedRateSum': row['CertifiedRateSum']
	})

output_file_path = os.path.join(output_dir, 'judged-data.json')
json_string = json.dumps(data_list, ensure_ascii=False, indent=2)
with open(output_file_path, "w", encoding='utf-8') as f:
	f.write(json_string)