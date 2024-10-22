# %%
import json, os, math
import pandas as pd

def sum_carditis_by_ages(data):
    df = pd.json_normalize(data)
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

json_file_path = os.path.join('../_datasets', 'carditis-reports.json')
with open(json_file_path, encoding='utf-8') as f:
    data = json.load(f)

(aged_df, unknown_ages_count, ages_count) = sum_carditis_by_ages(data)
print(aged_df)

print()
print(f'年齢不明:  {unknown_ages_count} 件')
print(f'年齢判明: {ages_count} 件')
