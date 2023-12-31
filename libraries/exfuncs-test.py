from exfuncs import (
	extract_vaccine_name_etc,
	extract_PT_names
)

# camelotを使ったデータ抽出において、やや複雑なパターンがあるため単体テストでそれらを確認する。

## 途中で行分割されず1行1データで表現されている行の場合
def test_extract_vaccine_name_etc_with_case1_a():
	case = {
		"days_to_onset": "不明",
    	"vaccine_name": "コミナティ筋注\nファイザー\nEY5422\n2回目",
	}
	dto, vn, mf, ln, vt = extract_vaccine_name_etc(case['days_to_onset'], case['vaccine_name'])
	assert dto == "不明" and vn == "コミナティ筋注" and mf == "ファイザー" and ln == "EY5422" and vt == "2回目"

def test_extract_vaccine_name_etc_with_case1_b():
	case = {
		"days_to_onset": "12 コミナティ筋注",
		"vaccine_name": "ファイザー\n不明\n2回目",
	}
	dto, vn, mf, ln, vt = extract_vaccine_name_etc(case['days_to_onset'], case['vaccine_name'])
	assert dto == "12" and vn == "コミナティ筋注" and mf == "ファイザー" and ln == "不明" and vt == "2回目"

def test_extract_vaccine_name_etc_with_case1_c():
	case = {
		"days_to_onset": "",
		"vaccine_name": "3 コミナティ筋注\nファイザー\nFN2723\n2回目",
	}
	dto, vn, mf, ln, vt = extract_vaccine_name_etc(case['days_to_onset'], case['vaccine_name'])
	assert dto == "3" and vn == "コミナティ筋注" and mf == "ファイザー" and ln == "FN2723" and vt == "2回目"

### case1_cと似ているが、末尾のロット番号と接種回数が「\n」ではなく半角スペースで区切られているパターン
def test_extract_vaccine_name_etc_with_case1_d():
	case = {
		"days_to_onset": "",
		"vaccine_name": "1 スパイクバックス筋注\nモデルナ\n000021A 3回目"
	}
	dto, vn, mf, ln, vt = extract_vaccine_name_etc(case['days_to_onset'], case['vaccine_name'])
	assert dto == "1" and vn == "スパイクバックス筋注" and mf == "モデルナ" and ln == "000021A" and vt == "3回目"

## 行の途中で複数行に分割されており、1つの列の要素に改行が含まれる行の場合
def test_extract_vaccine_name_etc_with_case2_a():
	case = {
	    "days_to_onset": "",
		"vaccine_name": "31 スパイクバックス筋注\nモデルナ\n3004228\n1回目\n3 スパイクバックス筋注\nモデルナ\n3005239\n2回目",
	}
	dto, vn, mf, ln, vt = extract_vaccine_name_etc(case['days_to_onset'], case['vaccine_name'])
	assert dto == "31\n3" and vn == "スパイクバックス筋注\nスパイクバックス筋注" and mf == "モデルナ\nモデルナ" and ln == "3004228\n3005239" and vt == "1回目\n2回目"

def test_extract_vaccine_name_etc_with_case2_b():
	case = {
	    "days_to_onset": "不明",
        "vaccine_name": "2 スパイクバックス筋注\nモデルナ\n不明\n2回目\nスパイクバックス筋注\nモデルナ\n不明\n1回目",
	}
	dto, vn, mf, ln, vt = extract_vaccine_name_etc(case['days_to_onset'], case['vaccine_name'])
	assert dto == "2\n不明" and vn == "スパイクバックス筋注\nスパイクバックス筋注" and mf == "モデルナ\nモデルナ" and ln == "不明\n不明" and vt == "2回目\n1回目"

def test_extract_vaccine_name_etc_with_case2_c():
	case = {
	    "days_to_onset": "不明\n不明",
        "vaccine_name": "スパイクバックス筋注\nモデルナ\n不明\n1回目\nスパイクバックス筋注\nモデルナ\n不明\n2回目\n2 スパイクバックス筋注\nモデルナ\n不明\n3回目",
	}
	dto, vn, mf, ln, vt = extract_vaccine_name_etc(case['days_to_onset'], case['vaccine_name'])
	assert dto == "不明\n不明\n2" and vn == "スパイクバックス筋注\nスパイクバックス筋注\nスパイクバックス筋注" and mf == "モデルナ\nモデルナ\nモデルナ" and ln == "不明\n不明\n不明" and vt == "1回目\n2回目\n3回目"

def test_extract_vaccine_name_etc_with_case2_d():
	case = {
	    "days_to_onset": "215 スパイクバックス筋注\n194 スパイクバックス筋注",
		"vaccine_name": "モデルナ\n不明\n1回目\nモデルナ\n不明\n2回目\n3 スパイクバックス筋注\nモデルナ\n3005840\n3回目",
	}
	dto, vn, mf, ln, vt = extract_vaccine_name_etc(case['days_to_onset'], case['vaccine_name'])
	assert dto == "215\n194\n3" and vn == "スパイクバックス筋注\nスパイクバックス筋注\nスパイクバックス筋注" and mf == "モデルナ\nモデルナ\nモデルナ" and ln == "不明\n不明\n3005840" and vt == "1回目\n2回目\n3回目"


def test_extract_PT_names_case_1():
	PT_names = extract_PT_names('後天性血友病（後天性血友病）\nコンパートメント症候群（コンパート\nメント症候群）\n関節痛（関節痛）\n筋肉内出血（筋肉内出血）\n皮膚変色（皮膚変色）')
	assert 5 == len(PT_names)
	assert '後天性血友病' == PT_names[0]
	assert 'コンパートメント症候群' == PT_names[1]
	assert '関節痛' == PT_names[2]
	assert '筋肉内出血' == PT_names[3]
	assert '皮膚変色' == PT_names[4]

def test_extract_PT_names_case_2():
	PT_names = extract_PT_names('ＣＯＶＩＤ−１９の疑い（ＣＯＶＩＤ\n−１９の疑い）\n薬効欠如（薬効欠如）')
	assert 2 == len(PT_names)
	assert 'ＣＯＶＩＤ−１９の疑い' == PT_names[0]
	assert '薬効欠如' == PT_names[1]