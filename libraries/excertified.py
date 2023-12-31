import unicodedata

'''
認定一覧などを抽出するための処理を集めた実装です。
'''

def extract_description_of_claim_etc(cel):
	'''
	認定一覧から性別、年齢、ワクチン名、請求内容を抽出する処理。

	Parameters
    ----------
    cel : string
        性別などの情報が入ったセルの文字列。
		  「女\n52歳 新型コロナ\n医療費・医療手当」
		上記のようなデータを想定する。
    
	Returns
    -------
	gender: string
	    性別
	age : int[]
	    年齢
	vaccine_name: string
	    ワクチン名
	description_of_claim: string
	    請求内容
	'''

	# todo: 配列のサイズ確認などをしていないが、ちょっと変わった
	# データの場合に例外が発生するかもしれない。その場合は修正する。
	array = cel.split('\n')
	gender = array[0]
	description_of_claim = array[2]

	sub_array = array[1].split(' ')
	age = []
	for a in sub_array[0].replace('歳', '').replace('、', ',').split(','):
		age.append(int(a))
	vaccine_name = sub_array[1]

	return gender, age, vaccine_name, description_of_claim


def sum_certified_and_repudiation_count(data):
	certified_count = 0
	repudiation_count = 0
	unknown = 0

	for d in data:
		if d['judgment_result'] == '認定':
			certified_count+=1
		elif d['judgment_result'] == '否認':
			repudiation_count+=1
		else:
			unknown+=1

	return certified_count, repudiation_count, unknown


def extract_judgment_result_etc_v1(cell):
	'''
	認定一覧から症状名、判定結果、否認理由、備考を抽出する処理。
	判定結果に関して「認定」「否認」「保留」すべてを抽出する版。

	Parameters
	----------
	cell: string
		判定結果などの情報が入ったセルの文字列。
		  「アナフィラキシー\n認定」
		  「否認\n3」
		上記のような文字列。否認の場合には症状名は空になるっぽい。
	
	Returns
	-------
	symptoms: string[]
		症状名（複数列挙されている場合あり、空の場合もあり）
	judgment_result: string
		判定結果
	reasons_for_repudiation: string
		否認理由
	remarks: string
		備考
	'''
	symptoms = []
	judgment_result = ''
	reasons_for_repudiation = ''
	remarks = ''

	array = cell.split('\n')
	if array[0] == '否認':
		judgment_result = array[0]
		reasons_for_repudiation = array[1]
		if len(array) > 2:
			remarks = ''.join(array[2,:])
		return symptoms, judgment_result, reasons_for_repudiation, remarks
	
	judgment_index = -1
	for index, s in enumerate(array):
		if s.find('認定') > -1 or s.find('保留') > -1:
			judgment_index = index
			judgment_result = s

	if judgment_index == -1:
		# 認定列は見つからなかった
		return symptoms, judgment_result, reasons_for_repudiation, remarks
	elif judgment_index == 0:
		# 先頭で「認定」または「保留」が見つかった（症状の記載無しの場合）
		judgment_result = array[0]
		if len(array) > 1:
			remarks = ''.join(array[1,:])
	else:
		for i in range(0, judgment_index):
			for sym_name in array[i].split('、'):
				symptoms.append(unicodedata.normalize("NFKC", sym_name))
		if len(array) > judgment_index + 1:
			remarks = ''.join(array[judgment_index+1,:])
		
	return symptoms, judgment_result, reasons_for_repudiation, remarks


def extract_reasons_for_repudiation(cell, rType):
	'''
	おおくが空白か1～5の数字1つという内容なのだが、たまに複数の数字が入力される場合あり。
	複数の場合、区切り文字に読点を使って「1、3」というように表現することもあれば、「1,2」
	というようにカンマを使う場合もあるようだった。
	（最初から、どの項目に複数入る可能性があるのか、複数の場合の区切り文字は・・といった
	データのスキーマを決めておいてほしいものだ。 >> 公開されている元データの作者）

	Parameters
	----------
	cell: string
		判定結果などの情報が入ったセルの文字列。
		  「1.0」
		  「1.0,2.0」
		空の場合も多い。ピリオドで区切られたパターンもあったため、int型にキャストして小数点
		以下の桁の処理をこちらの関数でやることにした。
	type: string
		否認理由が5段階の頃と4段階の頃があるのだが、同じ数字が別の意味になるような変更で
		あったため、それぞれの世代に便宜上の区別をするための「タイプ」文字列を付与して区別
		する必要が生じてしまった。「タイプ」を表す文字列。
	
	Returns
	-------
	reasons_for_repudiation: string[]
		否認理由（まれに複数列挙されている場合があるため配列で表現する。空の場合も多い。）
	'''
	# 区切り文字が読点「、」の場合や、タイポっぽく「.」の場合があるので、まずカンマに置換
	cell = cell.replace('、', ',').replace('.', ',')

	reasons_for_repudiation = []
	if cell != '':
		if len(cell.split(',')) > 1:
			for item in cell.split(','):
				# float型の小数点以下のゼロが抽出されてしまうので、ここで無視する
				if item == '0':
					continue
				reasons_for_repudiation.append(rType + '-' + item)
		else:
			reasons_for_repudiation.append(rType + '-' + cell)
	
	return reasons_for_repudiation
