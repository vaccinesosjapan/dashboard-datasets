import yaml, os
import pandas as pd

metadata_path = os.path.join("../carditis", "metadata.yaml")
with open(metadata_path, "r", encoding='utf-8') as f:
    metadata_root = yaml.safe_load(f) 
metadata = metadata_root['metadata']
expected_issues = metadata['expected_issues']

def sum_carditis_by_manufacturers(issues):
    df_m = pd.json_normalize(issues, meta='manufacturer', record_path='myocarditis')
    df_m = df_m.groupby('manufacturer', as_index=False).sum()
    df_m = df_m.drop(['name'], axis=1)
    df_m = df_m.sort_values('count', ascending=False)

    df_p = pd.json_normalize(issues, meta='manufacturer', record_path='pericarditis')
    df_p = df_p.groupby('manufacturer', as_index=False).sum()
    df_p = df_p.drop(['name'], axis=1)
    df_p = df_p.sort_values('count', ascending=False)
    
    return (df_m, df_p)

# %%
(df_m, df_p) = sum_carditis_by_manufacturers(expected_issues)

df_m_string = df_m.to_json(orient='records' ,force_ascii=False, indent=2)
print(df_m_string)

df_p_string = df_p.to_json(orient='records' ,force_ascii=False, indent=2)
print(df_p_string)