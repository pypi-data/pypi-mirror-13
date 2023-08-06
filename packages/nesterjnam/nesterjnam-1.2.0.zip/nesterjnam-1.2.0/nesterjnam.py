'''파이썬 연습용 모듈 배포'''

def print_lol(LIST,index=0):
    '''리스트 내의 리스트 있을때 출력 함수
    index인자 사용하여 들여쓰기 수준 결정'''
    for in_item in LIST:
        if isinstance(in_item,list):
            print_lol(in_item,index+1)
        else:
            for i in range(index):
                print('\t',end='')
            print(in_item)
