import json, os
import pandas as pd

json_file_path = os.path.join('../_datasets', 'death-reports.json')
with open(json_file_path, encoding='utf-8') as f:
    json_data = json.load(f)
    
df = pd.json_normalize(json_data)
df = df[["manufacturer", "causal_relationship_by_expert"]]
df['death_count'] = 1

merged_df = df.groupby(['manufacturer', 'causal_relationship_by_expert'], as_index=False).sum()
merged_df = merged_df[(merged_df['causal_relationship_by_expert'] == 'β') | (merged_df['causal_relationship_by_expert'] == 'γ')]
merged_df = merged_df.drop(columns=['causal_relationship_by_expert'])
merged_df = merged_df.groupby('manufacturer', as_index=False).sum()

# %%
merged_df.to_dict(orient='records')


