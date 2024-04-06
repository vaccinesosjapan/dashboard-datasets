import glob
import pandas as pd
import numpy as np

print('''# 手作業で修正が必要なデータ一覧

手作業で修正が必要な`onset_dates`を持つデータを一覧します。''')

json_file_path_list = glob.glob('reports-data/*.json')
for json_file_path in json_file_path_list:
	df = pd.read_json(json_file_path)

	def find_invalid_data(s: str):
		if s.find('\n') > -1 or s.find('※') > -1 or s.find('→') > -1 or s.find('後日') > -1:
			return True
		return False

	found = False
	osd_list = []
	osd_array = np.array(df['onset_dates'])
	for index, osd in enumerate(osd_array):
		for d in osd:
			if find_invalid_data(d):
				if not found:
					print()
					print(f"## {json_file_path}\n")

				d_no_line = str(d).replace('\n', '')
				print(f"- no: {df['no'][index]}, onset_date: {d_no_line}")
				found = True
