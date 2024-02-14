import json, os
import yaml

with open('metadata.yaml', "r", encoding='utf-8') as f:
    metadata_root = yaml.safe_load(f) 
metadata = metadata_root['metadata']
expected_issues = metadata['expected_issues']

carditis_issues = []
myocarditis_list = []
pericarditis_list = []
for issue in expected_issues:
	carditis_issues.append({
        "vaccine_name": issue['vaccine_name'],
        "myocarditis_count": issue['myocarditis_count'],
        "pericarditis_count": issue['pericarditis_count']
	})
	myocarditis_list.append(issue['myocarditis_count'])
	pericarditis_list.append(issue['pericarditis_count'])

sorted_issues = sorted(carditis_issues, key=lambda issue: issue['vaccine_name'])

myocarditis_sum = sum(myocarditis_list)
pericarditis_sum = sum(pericarditis_list)
total_sum = sum([myocarditis_sum, pericarditis_sum])

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
		"issues_with_vaccine_name": sorted_issues
	}
}

json_string = json.dumps(summary_data, ensure_ascii=False, indent=2)

output_path = os.path.join('../_datasets', 'carditis-summary.json')
with open( output_path, "w", encoding='utf-8') as f:
    f.write(json_string)