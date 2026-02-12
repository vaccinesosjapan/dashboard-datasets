import glob, os, subprocess
import pandas as pd

json_file_root_dir = "./reports-data"
json_file_list = glob.glob("*", root_dir=json_file_root_dir)

for json_file_name in json_file_list:
	print(f"source情報など付与中: {json_file_name}")
	subprocess.run([ "python", f"./_4-apply-source.py", json_file_name ])
	print()
