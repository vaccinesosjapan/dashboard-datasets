import re, sys, traceback

def extract_vaccine_name_etc(days_to_onset, vaccine_name):
	"""
    厚生労働省の心筋炎/心膜炎の報告一覧をPDFから抽出する際、6〜9列目の内容が
	思ったように抽出できない。そのため、この処理で分割する。
    
    Parameters
    ----------
    days_to_onset : string
        6列目（row[5]） の情報。
    vaccine_name : string
        7列目（row[6]） の情報。

    Returns
    -------
	dto: string
	    接種から発生までの日数（days_to_onset）
	vn : string
	    ワクチン名（vaccine_name）
	mf: string
	    製造販売業者（manufacturer）
	ln: string
	    ロットNo（lot_no）
	vt: string
	    接種回数（vaccinated_times）
    """
	# 複数行に渡るデータの可能性があり配列で返すことも考えたが、一旦は「\n」区切りの文字列にした。
	dto = ''
	vn = ''
	mf = ''
	ln = ''
	vt = ''

	separator = '\n'

	try:
		# 途中の列で複数行に分かれているデータの場合、ここでrow_countが2以上になる
		dtoArray = days_to_onset.split('\n')
		dUsedIndex = -1
		vnArray = vaccine_name.split('\n')
		vUsedIndex = -1
		if len(vnArray) == 0:
			return dto, vn, mf, ln, vt

		vn_first_item = vnArray[0]
		if __is_days_and_vaccine_name(vn_first_item):
			items = vn_first_item.split(' ')
			dto = items[0]
			vn = items[1]
			mf = vnArray[1]
			vUsedIndex = 1
		else:
			d_first_item = dtoArray[0]
			if __is_days_and_vaccine_name(d_first_item):
				items = d_first_item.split(' ')
				dto = items[0]
				vn = items[1]
				dUsedIndex = 0
				mf = vn_first_item
				vUsedIndex = 0
			else:
				dto = d_first_item
				vn = vn_first_item
				mf = vnArray[1]
				vUsedIndex = 1
		
		if __is_lot_no_and_vaccinated_times(vnArray[vUsedIndex+1]):
			items = vnArray[vUsedIndex+1].split(' ')
			ln = items[0]
			vt = items[1]
			vUsedIndex = vUsedIndex + 1
		else:
			ln = vnArray[vUsedIndex+1]
			vt = vnArray[vUsedIndex+2]
			vUsedIndex = vUsedIndex + 2
			
		if len(ln.split(' ')) > 1:
			ln = ln.split(' ')[0]

		if len(vnArray[vUsedIndex+1:]) > 0:
			dto2, vn2, mf2, ln2, vt2 = extract_vaccine_name_etc( '\n'.join(dtoArray[dUsedIndex+1:]), '\n'.join(vnArray[vUsedIndex+1:]) )
			dto = dto + separator + dto2
			vn = vn + separator + vn2
			mf = mf + separator + mf2
			ln = ln + separator + ln2
			vt = vt + separator + vt2

	except Exception as e:
		print("-"*60)
		print(f'failed to execute extract_vaccine_name_etc func with days_to_onset: {days_to_onset}, vaccine_name: {vaccine_name}')
		traceback.print_exc(file=sys.stderr)
		print("-"*60)
		print()
	
	return dto, vn, mf, ln, vt

def __is_days_and_vaccine_name(str):
	items = str.split(' ')
	return len(items) == 2 and items[0].isdecimal()

def __is_lot_no_and_vaccinated_times(str):
	return len(str.split(' ')) > 1


def extract_vaccine_name_with_mf(days_to_onset, vaccine_name, manufacturer):
	"""
    製造販売業者の副反応疑い報告一覧をPDFから抽出する際、「接種から発生までの日数」の内容に
	応じて列に入る内容が異なる挙動があったため、この関数で処理する。
    
    Parameters
    ----------
    days_to_onset : string
        6列目（row[5]） の情報。
    vaccine_name : string
        7列目（row[6]） の情報。
	manufacturer: string
	    8列目（row[7]）の情報。

    Returns
    -------
	dto: string
	    接種から発生までの日数（days_to_onset）
	vn : string
	    ワクチン名（vaccine_name）
	mf: string
	    製造販売業者名（manufacturer）
    """
	# 複数行に渡るデータの可能性があり配列で返すことも考えたが、一旦は「\n」区切りの文字列にした。
	dto = days_to_onset
	vn = ''.join(vaccine_name.split('\n'))
	mf = manufacturer

	try:
		vn_array = vn.split(' ')
		if len(vn_array) > 1:
			dto = vn_array[0]
			vn = vn_array[1]

		vn_array = vn.split('）')
		if len(vn_array) > 1:
			if vn_array[1] == '製販不明' and mf == '':
				mf = '製販不明'
				vn = vn_array[0] + '）'

	except Exception as e:
		print("-"*60)
		print(f'failed to execute extract_vaccine_name func with days_to_onset: {days_to_onset}, vaccine_name: {vaccine_name}')
		traceback.print_exc(file=sys.stderr)
		print("-"*60)
		print()
	
	return dto, vn, mf


def extract_age_gender(no, age):
	"""
    厚生労働省の心筋炎/心膜炎の報告一覧をPDFから抽出する際、2列目の内容が
	思ったように抽出できない。そのため、この処理で分割する。
    
    Parameters
    ----------
	no: string
	    1列名（row[0]）の情報。
    age : string
        2列目（row[1]）の情報。

    Returns
    -------
	n: int
	    No（No）
	ag: string
	    年齢（age）
	gd : string
	    性別（gender）
    """
	n = ''
	ag = ''
	gd = ''

	if no == '':
		array = age.split(' ')
		if len(array) > 0:
			n = array[0]
		if len(array) > 1:
			ag = array[1]
		if len(array) > 2:
			gd = array[2]
	else:
		n = no
		array = age.split(' ')
		if len(array) > 0:
			ag = array[0]
		if len(array) > 1:
			gd = array[1]
	
	# 27681※\n5 というようにこめじるし付きの場合に対応
	if len(n.split('※')) > 1:
		n = n.split('※')[0]
	if n != '' and n != '不明':
		n = int(n)
	
	if ag.find('歳代') == -1:
		ag = ag.replace('歳', '')

	return n, ag, gd


def split_normal(data):
	array = data.split('\n')
	for index, d in enumerate(array):
		array[index] = d.strip()
	return array


def extract_age_gender_with_check(no, age):
	"""
    厚生労働省の心筋炎/心膜炎の報告一覧をPDFから抽出する際、2列目の内容が
	思ったように抽出できない。そのため、この処理で分割する。
    
    Parameters
    ----------
	no: string
	    1列名（row[0]）の情報。
    age : string
        2列目（row[1]）の情報。

    Returns
    -------
	n: int
	    No（No）
	ag: string
	    年齢（age）
	gd : string
	    性別（gender）
    """
	n = ''
	ag = ''
	gd = ''

	if no == '':
		array = age.split(' ')
		if len(array) > 0:
			n = array[0]
		if len(array) > 1:
			ag = array[1]
		if len(array) > 2:
			gd = array[2]
	else:
		n = no
		array = age.split(' ')
		if len(array) > 0:
			ag = array[0]
		if len(array) > 1:
			gd = array[1]
	
	# 27681※\n5 というようにこめじるし付きの場合に対応
	if len(n.split('※')) > 1:
		n = n.split('※')[0]

	if n.isdecimal():
		n = int(n)
	
	if ag.find('歳代') == -1:
		ag = ag.replace('歳', '')

	return n, ag, gd

def extract_PT_names(PT):
	'''
	ＣＯＶＩＤ−１９の疑い（ＣＯＶＩＤ\n−１９の疑い）\n薬効欠如（薬効欠如）

	上記のような「項目の区切りだけではなく括弧の中にも改行が入る」パターンに対応
	するための関数。
	'''
	array = PT.split('\n')
	pre = ''
	post = ''
	pt_array = []
	for item in array:
		if item.find('（') > -1 and item.find('）') > -1:
			pt_array.append(item)
		elif item.find('（') > -1 and item.find('）') == -1:
			pre = item
		elif item.find('（') == -1 and item.find('）') > -1:
			post = item

		if pre != '' and post != '':
			pt_array.append(pre + post)
			pre = ''
			post = ''

	PT_names = []
	for pt in pt_array:
		matched = re.findall(r'(?<=（).*(?=）)', pt)
		if matched:
			for m in matched:
				PT_names.append(m)

	return PT_names


def split_pre_existing_disease_names(names):
	dNames = names.split(';\n')
	if len(dNames) == 1:
		dNames = names.split('; \n')
	return dNames


def extract_special_row_over_pages(row):
	'''
	ページをまたぐような複数行の項目の場合、列ヘッダと行の内容がくっついた状態で抽出される。
	このデータから、行のデータだけを抽出するメソッド。

	例）引数のデータは、以下のようなデータを想定する
	0                                       $ N\no $\n18864
	1                                                    年齢
	2                                                性別\n男性
	3                                       接種日\n2021/03/18
	4               発生日\n2021/12/04\n2021/12/04\n2021/12/04
	5                                       接種から\n発生までの\n日数
	6                                    ワクチン名\n261 コミナティ筋注
	7                                         製造販売業者\nファイザー
	8                                         ロット番号\nEP2163
	9     症状名（PT名） \n妊娠前の母体の曝露（妊娠前の母体の\n曝露）\n新生児呼吸窮迫症候群（...
	10                            転帰日\n未記入\n未記入\n2022/04/10
	11                                     転帰内容\n軽快\n軽快\n回復
	12                                          専門家の評価PT\n-
	13                                    専門家の\n因果関係評価※1\n-
	14                              専門家の\nブライトン分\n類レベル※2\n-
	15                                            専門家の意見\n-

	例）年齢が「◯◯歳代」の時には、なぜか年齢列の方にNoとageがまとまるので注意
	0                                            $ N\no $
	1                                      年齢\n20068 70歳代
	2                                                  性別
	3                                         接種日\n不明\n不明
	4                                       発生日\n未記入\n未記入
	5                                 接種から\n発生までの\n日数\n不明
	6                                      ワクチン名\nコミナティ筋注
	7                                       製造販売業者\nファイザー
	8                                           ロット番号\n不明
	9     症状名（PT名） \n新型コロナウイルス感染症（ＣＯＶＩ\nＤ−１９）\n薬効欠如（薬効欠如）
	10                                      転帰日\n未記入\n未記入
	11                                       転帰内容\n不明\n不明
	12                                        専門家の評価PT\n-
	13                                  専門家の\n因果関係評価※1\n-
	14                            専門家の\nブライトン分\n類レベル※2\n-
	15                                          専門家の意見\n-
	'''
	result = []
	no = ''
	age = ''
	gender = ''

	split_age = row[1].split('\n')
	if len(row[0].split('\n')) > 2:
		no = '\n'.join(row[0].split('\n')[2:])
	else:
		if len(split_age) > 1:
			if len(split_age[1].split(' ')) > 1:
				no = split_age[1].split(' ')[0]

	if len(split_age) > 1:
		if len(split_age[1].split(' ')) > 1:
				if len(row[0].split('\n')) > 2:
					age = split_age[1].split(' ')[0]
					gender = split_age[1].split(' ')[1]
				else:
					no = split_age[1].split(' ')[0]
					age = split_age[1].split(' ')[1]
		else:
			age = split_age[1]

	if len(row[2].split('\n')) > 1:
		gender = row[2].split('\n')[1]

	for index, item in enumerate(row):
		#print(f'index: {index}, result: {result}')
		if index == 0:
			result.append(no)
		elif index == 1:
			result.append(age)
		elif index == 2:
			result.append(gender)
		elif index == 13:
			if len(item.split('\n')) > 2:
				result.append('\n'.join(item.split('\n')[2:]))
			else:
				result.append('')
		elif index == 5 or index == 14:
			if len(item.split('\n')) > 3:
				result.append('\n'.join(item.split('\n')[3:]))
			else:
				result.append('')
		else:
			if len(item.split('\n')) > 1:
				result.append('\n'.join(item.split('\n')[1:]))
			else:
				result.append('')
	
	return result

# tests
def test_is_days_and_vaccine_name():
	assert __is_days_and_vaccine_name('3 スパイクバックス筋注') == True
	assert __is_days_and_vaccine_name('コミナティ筋注') == False

def test_is_lot_no_and_vaccinated_times():
	assert __is_lot_no_and_vaccinated_times('000021A 3回目') == True
	assert __is_lot_no_and_vaccinated_times('FN2723') == False