import json, os
import yaml
import pandas as pd

output_dir = '../_datasets'

with open('reports-settings-all.yaml', "r", encoding='utf-8') as file:
    settings_root = yaml.safe_load(file)
settings = settings_root['settings']

date_list = []
certified_list = []
repudiation_list = []

for setting in settings:
    date_list.append(setting['date'])
    certified_list.append(setting['expected_count']['certified'])
    repudiation_list.append(setting['expected_count']['repudiation'])

df = pd.DataFrame({'Date': date_list, 'CertifiedCount': certified_list, 'RepudiationCount': repudiation_list})
df['CertifiedRate'] = round(df['CertifiedCount'] / (df['CertifiedCount'] + df['RepudiationCount']) * 100, 2)
df['CertifiedCountSum'] = df['CertifiedCount'].cumsum()
df['RepudiationCountSum'] = df['RepudiationCount'].cumsum()
df['CertifiedRateSum'] = round( df['CertifiedCountSum'] / (df['CertifiedCountSum'] + df['RepudiationCountSum']) * 100, 2 )

data_list = []
rowCount = df.shape[0]
for rowIndex in range(0, rowCount):
	row = df.loc[rowIndex]
	data_list.append({
		'Date': row['Date'],
		'CertifiedCount': row['CertifiedCount'].item(),
		'RepudiationCount': row['RepudiationCount'].item(),
		'CertifiedRate': row['CertifiedRate'],
		'CertifiedCountSum': row['CertifiedCountSum'].item(),
		'RepudiationCountSum': row['RepudiationCountSum'].item(),
		'CertifiedRateSum': row['CertifiedRateSum']
	})

output_file_path = os.path.join(output_dir, 'judged-data.json')
json_string = json.dumps(data_list, ensure_ascii=False, indent=2)
with open(output_file_path, "w", encoding='utf-8') as f:
	f.write(json_string)


