#%%
import json, os, math
import pandas as pd

json_file_path = os.path.join('../_datasets', 'death-reports.json')
with open(json_file_path, encoding='utf-8') as f:
    json_data = json.load(f)

def sum_death_by_ages(data):
    df = pd.json_normalize(data)
    df['age'] = df['age'].map(lambda x: str(x).replace('歳代','').replace('歳','').replace('代',''))
    df = df[["age", "causal_relationship_by_expert"]]
    df = df[df['causal_relationship_by_expert'] != 'β']
    
    unknown_ages_count = df[~df['age'].str.isdecimal()].shape[0]
    df = df[df['age'].str.isdecimal()]
    df = df.drop(columns=['causal_relationship_by_expert'])
    ages_count = df.shape[0]
    
    df['age'] = df['age'].astype(int)
    df['generation'] = df['age'].apply(lambda x:math.floor(x/10)*10)
    df['count'] = 1
    df = df.drop(columns=['age'])
    
    aged_df = df.groupby('generation').sum()
    aged_df = aged_df.reset_index()
    aged_df['generation'] = aged_df['generation'].map(lambda x: str(x) + '代')
    aged_df = aged_df.rename(columns={'generation': 'x'})
    aged_df = aged_df.rename(columns={'count': 'y'})
    
    return (aged_df, ages_count, unknown_ages_count)

# %%
(aged_df, ages_count, unknown_ages_count) = sum_death_by_ages(json_data)

print('causal_relationship_by_expert が β の案件は除外')
print(f'年代が判別可能なデータは {ages_count} 件')
print(f'年代不明なデータは {unknown_ages_count} 件')
print(aged_df)