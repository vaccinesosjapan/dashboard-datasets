import glob, json, os
import yaml
import pandas as pd

output_dir = '../_datasets'


def sum_by_manufacturer():
    json_file_path = os.path.join('../_datasets', 'death-reports.json')
    with open(json_file_path, encoding='utf-8') as f:
        json_data = json.load(f)
    
    df = pd.json_normalize(json_data)
    df = df[["manufacturer", "causal_relationship_by_expert"]]
    df['death_count'] = 1
    
    merged_df = df.groupby(['manufacturer', 'causal_relationship_by_expert'], as_index=False).sum()
    merged_df = merged_df[(merged_df['causal_relationship_by_expert'] == 'β') | (merged_df['causal_relationship_by_expert'] == 'γ')]
    merged_df = merged_df.drop(columns=['causal_relationship_by_expert'])
    
    return merged_df.groupby('manufacturer', as_index=False).sum()

def sum_evaluations():
    death_issues = []
    alpha_count = 0
    beta_count = 0
    gamma_count = 0

    jsonFileList = glob.glob('summary-data/*.json')
    for file in jsonFileList:
        with open(file, "r", encoding='utf-8') as f:
            data = json.load(f)
            death_issues.append(data)
            alpha_count += data['evaluations']['alpha']
            beta_count += data['evaluations']['beta']
            gamma_count += data['evaluations']['gamma']
    
    sorted_issues = sorted(death_issues, key=lambda issue: issue['vaccine_name'])  
   
    return (sorted_issues, alpha_count, beta_count, gamma_count)


(sorted_issues, alpha_count, beta_count, gamma_count) = sum_evaluations()
total_count = alpha_count + beta_count + gamma_count

with open('summary-metadata.yaml', "r", encoding='utf-8') as file:
    metadata_root = yaml.safe_load(file)
metadata = metadata_root['metadata']

summary_data = {
	"death_summary": {
        "date": metadata['summary']['date'],
		"source": metadata['summary']['source'],
        "sum_by_evaluation": {
			"total": total_count,
			"alpha": alpha_count,
			"beta": beta_count,
			"gamma": gamma_count
		},
        "sum_by_vaccine_name": sorted_issues,
        "sum_by_manufacturer": sum_by_manufacturer().to_dict(orient='records')
	},
	"death_issues": {
        "date": metadata['issues']['date'],		
	}
}

json_string = json.dumps(summary_data, ensure_ascii=False, indent=2)
output_path = os.path.join(output_dir, 'death-summary.json')
with open( output_path, "w", encoding='utf-8') as f:
    f.write(json_string)