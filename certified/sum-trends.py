import json, os
import pandas as pd

output_dir = '../_datasets'

with open('../_datasets/certified-symptoms.json', encoding='utf-8') as f:
    d = json.load(f)
df = pd.json_normalize(d)

df_male = df.sort_values('counts.male', ascending=False).head(10)
df_male = df_male.drop(['counts.female', 'counts.sum'], axis=1)
df_male = df_male.rename(columns={'counts.male': 'count'})

df_female = df.sort_values('counts.female', ascending=False).head(10)
df_female = df_female.drop(['counts.male', 'counts.sum'], axis=1)
df_female = df_female.rename(columns={'counts.female': 'count'})

df_sum = df.sort_values('counts.sum', ascending=False).head(10)
df_sum = df_sum.drop(['counts.male', 'counts.female'], axis=1)
df_sum = df_sum.rename(columns={'counts.sum': 'count'})

trends_data = {
    'female_counts': json.loads(df_female.to_json(orient='records', force_ascii=False)),
    'male_counts': json.loads(df_male.to_json(orient='records', force_ascii=False)),
    'sum_counts': json.loads(df_sum.to_json(orient='records', force_ascii=False))
}
trends_data_string = json.dumps(trends_data, ensure_ascii=False, indent=2)

with open(os.path.join(output_dir, 'certified-trends.json'), 'w', encoding='utf-8') as f:
    f.write(trends_data_string)