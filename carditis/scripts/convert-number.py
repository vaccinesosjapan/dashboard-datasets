import sys, json, os

json_file_path = sys.argv[1]
from_number = int(sys.argv[2])
add_number = int(sys.argv[3])

with open(json_file_path, "r", encoding='utf-8') as f:
	json_data = json.load(f)

converted_data = []
for item in json_data:
	item_no = item['no']
	if item_no >= from_number:
		item['no'] = item_no + add_number
	converted_data.append(item)

json_string = json.dumps(converted_data, ensure_ascii=False, indent=2)
file_name = json_file_path.rsplit('\\', 1)[1].rsplit('.json', 1)[0]
output_path = os.path.join('reports-data', file_name + '-converted.json')
with open( output_path, "w", encoding='utf-8') as f:
    f.write(json_string)