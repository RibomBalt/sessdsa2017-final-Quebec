from table import *
# tb为TableData类型的对象
# ds为函数可以利用的存储字典
# 函数需要返回一个RacketAction对象

# 当前table是假的！是为了阻止报错放的一个旧版table！

def play(tb:TableData, ds:dict):
    '''
    主函数，每次游戏进程会调用这个函数
    :param tb: 桌面数据，
    :param ds: 
    :return: 
    '''
    # return RacketAction(tb.tick, tb.ball['position'].y - tb.side['position'].y, 0, 0)
    pass