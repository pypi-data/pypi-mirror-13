'''파이썬 연습용 모듈 배포'''

def print_lol(LIST,indent=False,index=0):
    '''리스트 내의 리스트 있을때 출력 함수
    index인자 사용하여 들여쓰기 수준 결정
    indent인자 사용하여 들여쓰기 여부 결정'''
    for in_item in LIST:
        if isinstance(in_item,list):
            print_lol(in_item,indent,index+1)
        else:
            if indent:
                print('\t'*index,end='')
            print(in_item)
