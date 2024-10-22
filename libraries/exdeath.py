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
