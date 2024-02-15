import json, os, unicodedata
import yaml

with open('metadata.yaml', "r", encoding='utf-8') as f:
    metadata_root = yaml.safe_load(f) 
metadata = metadata_root['metadata']
expected_issues = metadata['expected_issues']


myocarditis_dict = dict()
pericarditis_dict = dict()
for issue in expected_issues:
    myocarditis_list = issue['myocarditis']
    for item in myocarditis_list:
        if item['count'] == 0:
            continue
        vaccine_name = unicodedata.normalize("NFKC", item['name'])
        mVal = myocarditis_dict.get(vaccine_name, 0)
        myocarditis_dict[vaccine_name] = mVal + item['count']

    pericarditis_list = issue['pericarditis']
    for item in pericarditis_list:
        if item['count'] == 0:
            continue
        vaccine_name = unicodedata.normalize("NFKC", item['name'])
        pVal = pericarditis_dict.get(vaccine_name, 0)
        pericarditis_dict[vaccine_name] = pVal + item['count']

carditis_issues = []
for key in sorted(myocarditis_dict.keys()):
	carditis_issues.append({
		"vaccine_name": key,
		"myocarditis_count": myocarditis_dict.get(key, 0),
		"pericarditis_count": pericarditis_dict.get(key, 0)
	})

sorted_issues = sorted(carditis_issues, key=lambda issue: issue['vaccine_name'])

myocarditis_sum = sum(myocarditis_dict.values())
pericarditis_sum = sum(pericarditis_dict.values())
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