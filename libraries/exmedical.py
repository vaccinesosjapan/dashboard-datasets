import unicodedata

def create_graph_by_causal_relationship(issues):
	graph = dict()

	for issue in issues:
		cr = issue['causal_relationship']
		if cr == '':
			if '(空白)' in graph:
				graph['(空白)'] += 1
			else:
				graph['(空白)'] = 1
		else:
			if cr in graph:
				graph[cr] += 1
			else:
				graph[cr] = 1
	
	sorted_list = sorted(graph.items(), key=lambda x: x[1], reverse=True)
	return dict(sorted_list)


def create_graph_severities_of_related(issues):
	graph = dict()

	for issue in issues:
		if issue['causal_relationship'].find('関連あり') == -1:
			continue
		sv = issue['severity']
		if sv == '':
			if '(空白)' in graph:
				graph['(空白)'] += 1
			else:
				graph['(空白)'] = 1
		else:
			if sv in graph:
				graph[sv] += 1
			else:
				graph[sv] = 1
	
	sorted_list = sorted(graph.items(), key=lambda x: x[1], reverse=True)
	return dict(sorted_list)


def cleansing_vaccine_name(vaccine_name):
	'''
	vaccine_nameの抽出文字列において、変なところに改行が入っているケースが
	多々ある。規則性があるわけでもないので、対処療法的に特定パターンに対して
	変換処理を実施する。
	'''
	vaccine_name = vaccine_name.replace('\n歳用', '歳用')
	vaccine_name = vaccine_name.replace('歳\n用', '歳用')
	vaccine_name = vaccine_name.replace('１\n価', '１価')
	vaccine_name = vaccine_name.replace('２\n価', '２価')
	vaccine_name = vaccine_name.replace('価\n不明', '価不明')
	vaccine_name = vaccine_name.replace('\n起源株', '起源株')
	vaccine_name = vaccine_name.replace('起\n源株', '起源株')
	vaccine_name = vaccine_name.replace('起源\n株', '起源株')
	vaccine_name = vaccine_name.replace('株\nBA.1', '株BA.1')
	vaccine_name = vaccine_name.replace('BA.4-\n5', 'BA.4-5')
	vaccine_name = vaccine_name.replace('11歳用\n（', '11歳用（')
	vaccine_name = vaccine_name.replace('オミクロ\nン', 'オミクロン')
	vaccine_name = vaccine_name.replace('オミ\nクロン', 'オミクロン')
	vaccine_name = vaccine_name.replace('オミクロン株\nXBB', 'オミクロン株XBB')
	vaccine_name = vaccine_name.replace('オ\nミクロン株', 'オミクロン株')

	return unicodedata.normalize("NFKC", vaccine_name)


def create_unique_list(original_list):
	'''
	DataFrameの場合 df['gender'].unique().tolist() のようにすればユニークな
	リストが得られるはずだが、それで得た項目をさらに改行で分割しつつユニーク
	なリストに再構成したい場合が多々あった。そのための処理。
	'''
	result_list = list()
	for item in original_list:
		for data in item.split('\n'):
			result_list.append(data)
	
	return list(set(result_list))


def create_unique_list_with_2d_list(original_2d_list):
	'''
	DataFrameから取り出した値がさらに配列の場合に使う想定。2次元配列を1次元に
	分解・再構成しながらユニークな1次元のリストにする。
	'''
	result_list = list()
	for item_list in original_2d_list:
		for item in item_list:
			result_list.append(item)
	
	return list(set(result_list))