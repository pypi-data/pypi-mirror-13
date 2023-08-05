'''
movie=[['The Holy Grail',1975,'Terry Jone&Terry Gilliam',91,
        ['Graham Chapman',['Michael Palin','John Cleese','Terry Gilliam','Eroc Idel','Terry Jones']]],
       ['The life of Brian',1979],
       ['The meaning of Life',1983]]
'''
'''
这是一个‘n1.py’模块，提供一个名为f1()的函数，作用是打印列表，其中可能包含（也可能不包含）
嵌套列表
'''

def f1(movie):

    '''
    使指定列表中的每个数据项（递归地）输出到屏幕上，各数据各占一行
    '''
    for a in movie:
        if isinstance(a,list):
            f1(a)
        else:
            print(a)
#f1(movie)
