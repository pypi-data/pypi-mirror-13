'''파이썬 연습용 모듈 배포'''

def print_list(LIST):
    '''리스트 내의 리스트 있을때 출력 함수'''
    for in_item in LIST:
        if isinstance(in_item,list):
            print_list(in_item)
        else:
            print(in_item)
