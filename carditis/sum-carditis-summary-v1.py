import json, os, unicodedata
import yaml
import pandas as pd
import numpy as np

with open('metadata.yaml', "r", encoding='utf-8') as f:
    metadata_root = yaml.safe_load(f) 
metadata = metadata_root['metadata']
expected_issues = metadata['expected_issues']

json_file_path = os.path.join('../_datasets', 'carditis-reports.json')
with open(json_file_path, encoding='utf-8') as f:
    json_data = json.load(f)


def sum_carditis_by_vaccine_name(issues):
    df_m = pd.json_normalize(issues, meta='manufacturer', record_path='myocarditis')
    df_p = pd.json_normalize(issues, meta='manufacturer', record_path='pericarditis')
    df_m = df_m.rename(columns={'count': 'myocarditis_count'})
    df_p = df_p.rename(columns={'count': 'pericarditis_count'})
    
    merged_df = pd.merge(df_m, df_p, on=['name', 'manufacturer'])
    merged_df = merged_df.groupby('name', as_index=False).sum()
    merged_df = merged_df.drop(['manufacturer'], axis=1)
    merged_df['name'] = merged_df['name'].map(lambda x: unicodedata.normalize("NFKC", str(x)))
    merged_df = merged_df.rename(columns={'name': 'vaccine_name'})
    
    return merged_df

def sum_carditis_by_manufacturers(issues):
    df_m = pd.json_normalize(issues, meta='manufacturer', record_path='myocarditis')
    df_p = pd.json_normalize(issues, meta='manufacturer', record_path='pericarditis')
    df_m = df_m.rename(columns={'count': 'myocarditis_count'})
    df_p = df_p.rename(columns={'count': 'pericarditis_count'})
    
    merged_df = pd.merge(df_m, df_p, on=['name', 'manufacturer'])
    merged_df = merged_df.groupby('manufacturer', as_index=False).sum()
    merged_df = merged_df.drop(['name'], axis=1)
    
    return merged_df

def sum_carditis_by_ages(data):
    df = pd.json_normalize(data)
    df['age'] = df['age'].map(lambda x: str(x).replace('歳代','').replace('歳','').replace('代',''))
    df = df[["age", "gender", "evaluated_PT"]]
    
    unknown_ages_count = df[df['age'] == ''].shape[0]

    df = df[df['age'] != '']
    df['age'] = df['age'].astype(int)
    ages_count = df.shape[0]
    
    labels = [ "{0}代".format(i) for i in range(0, 110, 10) ]
    c = pd.cut(df['age'], bins=np.arange(0, 111, 10), labels=labels)
    
    aged_df = df.groupby(c, as_index=False).agg(['count'])['age']
    aged_df = aged_df.reset_index()
    aged_df.to_dict(orient='records')

    return (aged_df, unknown_ages_count, ages_count)

df_by_m = sum_carditis_by_manufacturers(expected_issues)
myocarditis_sum = int(df_by_m['myocarditis_count'].sum())
pericarditis_sum = int(df_by_m['pericarditis_count'].sum())
total_sum = myocarditis_sum + pericarditis_sum

df_by_v = sum_carditis_by_vaccine_name(expected_issues)

(aged_df, unknown_ages_count, ages_count) = sum_carditis_by_ages(json_data)

summary_data = {
	"carditis_summary": {
		"date": metadata['summary']['commission_of_inquiry_date'],
		"total": total_sum,
		"myocarditis": myocarditis_sum,
		"pericarditis": pericarditis_sum,
		"source": metadata['summary']['source'],
	},
	"carditis_issues": {
        "date": metadata['summary']['data_end_date'],
		"issues_with_vaccine_name": df_by_v.to_dict(orient='records'),
        "issues_by_manufacturers": df_by_m.to_dict(orient='records'),
        "issues_by_ages": {
            "ages_count": ages_count,
            "unknown_ages_count": unknown_ages_count,
            "issues": aged_df.to_dict(orient='records')
        }
	}
}

json_string = json.dumps(summary_data, ensure_ascii=False, indent=2)
output_path = os.path.join('../_datasets', 'carditis-summary.json')
with open( output_path, "w", encoding='utf-8') as f:
    f.write(json_string)