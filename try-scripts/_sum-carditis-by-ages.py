# %%
import json, os
import pandas as pd
import numpy as np

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

json_file_path = os.path.join('../_datasets', 'carditis-reports.json')
with open(json_file_path, encoding='utf-8') as f:
    data = json.load(f)

(aged_df, unknown_ages_count, ages_count) = sum_carditis_by_vaccine_ages(data)
print(aged_df)

print()
print(f'年齢不明:  {unknown_ages_count} 件')
print(f'年齢判明: {ages_count} 件')
