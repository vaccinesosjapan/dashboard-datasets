from excertified import (
	extract_description_of_claim_etc
)

def test_extract_description_of_claim_etc ():
	cell = '女\n41歳 新型コロナ\n医療費・医療手当'
	gender, age, vaccine_name, description_of_claim = extract_description_of_claim_etc(cell)
	assert gender == '女' and age == [41] and vaccine_name == '新型コロナ' and description_of_claim == '医療費・医療手当'