# 교재 73쪽 파이썬 모듈 주석

""" 이 모듈은 "nester.py"로서
    중첩 리스트를 포함하기도 하는 theList 리스트를
    화면에 출력하는 print_lol() 함수를 정의한다. """

def print_lol(theList, level):
    """ 이 함수는 "theList"라는 단일 위치 지정 매개변수를 입력받는데,
        이 매개변수는 파이썬의 리스트 자료형에 해당하며
        내부에 하위 리스트를 포함한 중첩 리스트일 수도 있다.
        이 리스트 내부에 포함된 모든 자료 항목은 화면에 재귀적으로 출력된다. 
    """
    for item in theList:
        if isinstance(item, list):
            print_lol(item, level+1)
        else:
            print("%s %s" % ('\t'*level, item))

### 사용 방법
##movies = [    "The Holy Grails", 1975, "Terry Jones & Terry Gilliam", 91,
##                 [  "Graham Chapman",
##                    [   "Michael Palin", "John Cleese", "Terry Gilliam", "Eric Idle", "Terry Jones"
##                    ],
##                    4.5
##                 ], 1994
##            ]
##print_lol(movies, 0)

