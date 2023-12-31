from exdeath import (
	create_graph_data_list_by_age,
	extract_lot_no_etc
)

def test_create_graph_data_list_by_age():
	data = [
		{
			"age": "71歳",
			"causal_relationship_by_expert": "γ",
		},
		{
			"age": "99歳",
			"causal_relationship_by_expert": "γ",
		},
		{
			"age": "20歳",
			"causal_relationship_by_expert": "β",
		},
		{
			"age": "79歳",
			"causal_relationship_by_expert": "γ",
		},
		{
			"age": "20歳",
			"causal_relationship_by_expert": "α",
		},
	]

	result = create_graph_data_list_by_age(data)

	assert result[0].get('x') == '20代' and result[0].get('y') == 1
	assert result[1].get('x') == '70代' and result[1].get('y') == 2
	assert result[2].get('x') == '90代' and result[0].get('y') == 1

# きれいに各列にデータが入ってる系
def test_extract_lot_no_etc_1():
	col2 = "女"
	col3 = "2022年10月27日"
	col4 = "2022年10月27日"
	col5 = "GD9136"

	gender, vaccinated_dates, onset_dates, lot_no = extract_lot_no_etc(col2, col3, col4, col5)

	assert gender == '女'
	assert vaccinated_dates == "2022年10月27日"
	assert onset_dates == ['2022年10月27日']
	assert lot_no == 'GD9136'

# 接種日が空っぽになってる系
def test_extract_lot_no_etc_2():
	col2 = "女"
	col3 = ""
	col4 = "2022年11月20日 2022年11月22日 GJ1842"
	col5 = ""

	gender, vaccinated_dates, onset_dates, lot_no = extract_lot_no_etc(col2, col3, col4, col5)

	assert gender == '女'
	assert vaccinated_dates == "2022年11月20日"
	assert onset_dates == ['2022年11月22日']
	assert lot_no == 'GJ1842'

# 症状発生日の列が空っぽになってる系
def test_extract_lot_no_etc_3():
	col2 = '女'
	col3 = "2022年11月18日 2022年12月5日"
	col4 = ""
	col5 = "GJ1857"

	gender, vaccinated_dates, onset_dates, lot_no = extract_lot_no_etc(col2, col3, col4, col5)

	assert gender == '女'
	assert vaccinated_dates == "2022年11月18日"
	assert onset_dates == ['2022年12月5日']
	assert lot_no == 'GJ1857'

# ロット番号が空っぽになってる系
def test_extract_lot_no_etc_4():
	col2 = "男"
	col3 = "2022年11月9日"
	col4 = "2022年11月11日 GD9571"
	col5 = ""

	gender, vaccinated_dates, onset_dates, lot_no = extract_lot_no_etc(col2, col3, col4, col5)

	assert gender == '男'
	assert vaccinated_dates == "2022年11月9日"
	assert onset_dates == ['2022年11月11日']
	assert lot_no == 'GD9571'

# 全部空っぽになってる系（前の行の続きの行の場合など）
def test_extract_lot_no_etc_5():
	col2 = ""
	col3 = ""
	col4 = ""
	col5 = ""

	gender, vaccinated_dates, onset_dates, lot_no = extract_lot_no_etc(col2, col3, col4, col5)

	assert gender == ""
	assert vaccinated_dates == ""
	assert onset_dates == []
	assert lot_no == ''

def test_extract_lot_no_etc_6():
	col2 = "不明 2021年6月9日"
	col3 = ""
	col4 = "2021年6月16日"
	col5 = "不明"

	gender, vaccinated_dates, onset_dates, lot_no = extract_lot_no_etc(col2, col3, col4, col5)

	assert gender == '不明'
	assert vaccinated_dates == "2021年6月9日"
	assert onset_dates == ['2021年6月16日']
	assert lot_no == '不明'