import re, sys, traceback

def extract_lot_no_etc(col2, col3, col4, col5):
	'''
	死亡事例一覧の「接種日」「症状発生日」「ロット番号」の列を使う際、症状発生日やロット番号が
	空っぽの場合がある。これらに対処するため、専用の処理を実装して抽出する。
	「性別」が不明の場合に、接種日が性別の列に抽出されてしまうため、それも引数にもらって判断が
	必要になった。
	'''
	gender = ''
	vaccinated_dates = ''
	onset_dates = []
	lot_no = ''

	if col3 == '':
		if col2.split(' ')[0] == '不明':
			gender = '不明'
			if len(col2.split(' ')) > 1:
				vaccinated_dates = col2.split(' ')[1]
			onset_dates.append(col4)
			lot_no = col5
		else:
			gender = col2
			dates = col4.split(' ')
			if len(dates) > 2:
				vaccinated_dates = dates[0]
				onset_dates.append(dates[1])
				lot_no = dates[2]
			elif len(dates) > 1:
				vaccinated_dates = dates[0]
				onset_dates.append(dates[1])
			elif len(dates) > 0:
				vaccinated_dates = dates[0]
	elif col4 == '':
		gender = col2
		dates = col3.split(' ')
		if len(dates) > 1:
			vaccinated_dates = dates[0]
			onset_dates.append(dates[1])
		elif len(dates) == 1:
			vaccinated_dates = dates[0]
		else:
			vaccinated_dates = ''
		
		lot_no = col5
	elif col5 == '':
		gender = col2
		vaccinated_dates = col3
		dates = col4.split(' ')
		for d in dates:
			if d.find('月') > -1:
				onset_dates.append(d)
			else:
				lot_no = d
	else:
		gender = col2
		vaccinated_dates = col3
		onset_dates = col4.split(' ')
		lot_no = col5
	
	return gender, vaccinated_dates, onset_dates, lot_no


def create_graph_data_list_by_age(data):
	'''
	10代、20代などざっくりした年齢に対して人数をカウントして返す。

	Parameters
    ----------
    data: []
		PDFから抽出した死亡事例の一覧情報

    Returns
    -------
	result: dict
		{'0代': 1, '10代': 17, (以下略
	'''

	result = dict()
	for d in data:
		if d['causal_relationship_by_expert'] == 'β':
			# ワクチンと死亡が否定されているものだけ除外
			continue

		dAge = d['age']
		if type(dAge) is str:
			dAge = dAge.replace('代', '')
			if dAge.isdecimal():
				dAge = int(dAge)
			else:
				# 年齢が数字でなく変換もできないので除外
				continue

		generation = select_ages(dAge)
		if generation in result:
			result[generation] += 1
		else:
			result[generation] = 1
	
	# 文字列のままだと10代, 100代, 20代・・という順になるので、一旦数字にしてソート
	result_list = sorted(result.items(), key=lambda x: int(x[0].replace('代', '')))

	age_list = []
	for r in result_list:
		age_list.append({'x': r[0], 'y': r[1]})

	return age_list


def select_ages(age):
	if 0 <= age < 10:
		return '0代'
	elif 10 <= age < 20:
		return '10代'
	elif 20 <= age < 30:
		return '20代'
	elif 30 <= age < 40:
		return '30代'
	elif 40 <= age < 50:
		return '40代'
	elif 50 <= age < 60:
		return '50代'
	elif 60 <= age < 70:
		return '60代'
	elif 70 <= age < 80:
		return '70代'
	elif 80 <= age < 90:
		return '80代'
	elif 90 <= age < 100:
		return '90代'
	elif 100 <= age < 110:
		return '100代'
	elif 110 <= age < 120:
		return '110代'
	elif 120 <= age < 130:
		return '120代'
	else:
		print(f'特殊な年齢: {age}')
		return '長寿'