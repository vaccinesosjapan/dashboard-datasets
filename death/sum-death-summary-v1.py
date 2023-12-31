import glob, json, os
import yaml

jsonFileList = glob.glob('summary-data/*.json')
output_dir = '../_datasets'

death_issues = []
alpha_list = []
beta_list = []
gamma_list = []
for file in jsonFileList:
	with open(file, "r", encoding='utf-8') as f:
		data = json.load(f)
		death_issues.append(data)
		alpha_list.append(data['evaluations']['alpha'])
		beta_list.append(data['evaluations']['beta'])
		gamma_list.append(data['evaluations']['gamma'])

sorted_issues = sorted(death_issues, key=lambda issue: issue['vaccine_name'])

alpha_sum = sum(alpha_list)
beta_sum = sum(beta_list)
gamma_sum = sum(gamma_list)
total_sum = sum([alpha_sum, beta_sum, gamma_sum])

with open('summary-metadata.yaml', "r", encoding='utf-8') as file:
    metadata_root = yaml.safe_load(file)

metadata = metadata_root['metadata']

summary_data = {
	"death_summary": {
        "date": metadata['summary']['date'],
		"source": metadata['summary']['source'],
        "sum_by_evaluation": {
			"total": total_sum,
			"alpha": alpha_sum,
			"beta": beta_sum,
			"gamma": gamma_sum
		},
        "sum_by_vaccine_name": sorted_issues
	},
	"death_issues": {
        "date": metadata['issues']['date'],		
	}
}

json_string = json.dumps(summary_data, ensure_ascii=False, indent=2)
output_path = os.path.join(output_dir, 'death-summary.json')
with open( output_path, "w", encoding='utf-8') as f:
    f.write(json_string)