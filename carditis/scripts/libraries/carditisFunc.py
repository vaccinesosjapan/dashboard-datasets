import glob, json

def sum_carditis_reports(file_name_prefix, data_type):
	jsonFileList = glob.glob(f'reports-data/{file_name_prefix}-{data_type}*.json')

	carditis_reports = []
	for file in jsonFileList:
		with open(file, "r", encoding='utf-8') as f:
			data = json.load(f)
			carditis_reports += data

	return sorted(carditis_reports, key=lambda issue: issue['vaccine_name'])