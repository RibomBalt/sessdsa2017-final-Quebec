from table import *
import random

# 发球函数，总是做为West才发球
# ds为函数可以利用的存储字典
# 函数需要返回球的y坐标，和y方向的速度
def serve(ds:dict) -> tuple:
    return BALL_POS[1], BALL_V[1]

# 打球函数
# tb为TableData类型的对象
# ds为函数可以利用的存储字典
# 函数需要返回一个RacketAction对象
def play(tb:TableData, ds:dict) -> RacketAction:
    final_pos = random.sample([i for i in range(DIM[3]) if (i - tb.ball['position'].y) % 1800 ==0], 1)[0]
    final_v1 = random.sample([i for i in range(DIM[3] + 1, 3*DIM[3] - 1) if (i - tb.ball['position'].y) % 1800 ==0], 1)[0]
    final_v2 = random.sample([i for i in range(-2*DIM[3]+1, -1) if (i - tb.ball['position'].y) % 1800 ==0], 1)[0]
    final_v = (random.sample([final_v1, final_v2], 1)[0] - tb.ball['position'].y) // 1800
    return RacketAction(tb.tick, tb.ball['position'].y - tb.side['position'].y, final_v - tb.ball['velocity'].y, final_pos-tb.ball['position'].y, None, None)

# 对局后保存历史数据函数
# ds为函数可以利用的存储字典
# 本函数在对局结束后调用，用于双方分析和保存历史数据
def summarize(tick:int, winner:str, reason:str, west:RacketData, east:RacketData, ball:BallData, ds:dict):
    return
