import sys, unicodedata
import yaml
sys.path.append("./libraries")
from carditisFunc import (
	sum_carditis_reports
)

with open('metadata.yaml', "r", encoding='utf-8') as file:
    metadata_root = yaml.safe_load(file)
metadata = metadata_root['metadata']
expected_issues = metadata['expected_issues']

data_types = ['myocarditis', 'pericarditis']
for issue in expected_issues:
	for dType in data_types:
		file_name_prefix = issue['file_name_prefix']

		print(f'# prefix: {file_name_prefix}')
		print(f'## {dType}')
		sorted_reports = sum_carditis_reports(file_name_prefix, dType)

		data_dict = dict()
		for item in sorted_reports:
			vaccine_name = unicodedata.normalize("NFKC", item['vaccine_name'].split('\n')[0])
			val = data_dict.get(vaccine_name, 0)
			data_dict[vaccine_name] = val + 1

		expected_list = issue[dType]
		total_count = 0
		for item in expected_list:
			item_name = unicodedata.normalize("NFKC", item['name'])
			item_count = item['count']
			if data_dict.get(item_name, 0) != item_count:
				print(f'\033[33m[警告]\033[0m {item_name}: expected={item_count}, got={data_dict.get(item_name, 0)}')
			else:
				print(f'{item_name}: {data_dict.get(item_name, 0)}')
			
			total_count += item_count
		
		if total_count != len(sorted_reports):
			print(f'\033[33m[警告]\033[0m 合計: expected={total_count}, got={len(sorted_reports)}')
		else:
			print(f'合計: {len(sorted_reports)}')
		
		print()
