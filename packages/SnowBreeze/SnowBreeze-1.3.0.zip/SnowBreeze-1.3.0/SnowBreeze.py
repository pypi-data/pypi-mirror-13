# 파이썬 공부용 함수입니다.
# 본 함수는 the_list라는 이름의 인자를 갖고 있으며, 각 파이썬 리스트들을
# 각각의 항목별로 출력합니다. 내부 리스트는 재귀적으로 풀어서 출력됩니다.
# 세 번째 인자는 지정된 숫자만큼 탭을 시켜줍니다.
# 두 번째 인자는 들여쓰기 기능 여부를 확인합니다.

def print_lol(the_list, indent=False, level=0):
    for each_item in the_list:
        if isinstance(each_item, list):
            print_lol(each_item, indent, level+1)
        else:
            if indent :
                for tab_stop in range(level):
                    print("\t", end='')
            print(each_item)
