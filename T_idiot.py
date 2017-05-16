from table import *


# tb为TableData类型的对象
# ds为函数可以利用的存储字典
# 函数需要返回一个RacketAction对象
def play(tb, ds):
    return RacketAction(tb.tick, tb.ball['position'].y - tb.side['position'].y,
                        0, 0)
