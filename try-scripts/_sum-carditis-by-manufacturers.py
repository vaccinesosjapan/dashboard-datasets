import yaml, os
import pandas as pd

metadata_path = os.path.join("../carditis", "metadata.yaml")
with open(metadata_path, "r", encoding='utf-8') as f:
    metadata_root = yaml.safe_load(f) 
metadata = metadata_root['metadata']
expected_issues = metadata['expected_issues']

def sum_carditis_by_manufacturers(issues):
    df_m = pd.json_normalize(issues, meta='manufacturer', record_path='myocarditis')
    df_p = pd.json_normalize(issues, meta='manufacturer', record_path='pericarditis')
    df_m = df_m.rename(columns={'count': 'myocarditis_count'})
    df_p = df_p.rename(columns={'count': 'pericarditis_count'})
    
    merged_df = pd.merge(df_m, df_p, on=['name', 'manufacturer'])
    merged_df = merged_df.groupby('manufacturer', as_index=False).sum()
    merged_df = merged_df.drop(['name'], axis=1)
    
    return merged_df

# %%
merged_df = sum_carditis_by_manufacturers(expected_issues)
merged_df_string = merged_df.to_json(orient='records' ,force_ascii=False, indent=2)

print(merged_df_string)
