import subprocess
import os, sys

script_dir = os.path.dirname(os.path.abspath(__file__))

# ダッシュボードで直接使うデータ
sum_certified_path = os.path.join(script_dir, 'scripts', 'sum-certified-reports-v2.py')
sum_judged_data_path = os.path.join(script_dir, 'scripts', 'sum-judged-data.py')
sum_trends_path = os.path.join(script_dir, 'scripts', 'sum-trends.py')
sum_split_issues_path = os.path.join(script_dir, 'scripts', 'sum-split-issues.py')

subprocess.run([sys.executable, sum_certified_path], cwd=script_dir)
subprocess.run([sys.executable, sum_judged_data_path], cwd=script_dir)
subprocess.run([sys.executable, sum_trends_path], cwd=script_dir)
subprocess.run([sys.executable, sum_split_issues_path], cwd=script_dir)

# 参考データ
# ダッシュボードでCSVとしてダウンロードすれば、ソースURLなども含む「より完全なCSVデータ」が
# ダウンロード可能なため、この処理は不要。
#sum_csv_files_path = os.path.join(script_dir, 'scripts', 'sum-csv-files.py')
#subprocess.run([sys.executable, sum_csv_files_path], cwd=script_dir)