from table import *

def ball_v_range(y):
    """
    根据我方出射点坐标，算出y轴可取速度的边界值
    :param tb.step: 1800 tick
    :param Y: 镜像点y坐标
    :param height: 乒乓球桌的宽度, DIM[3] - DIM[2]
    :return: 与桌碰撞次数
    """
    height = DIM[3] - DIM[2]
    # v0,v1,v2,v3是速度的范围边界:v0-v1,v2-v3可取
    v0 = (3 * height - y) // 1800
    v1 = (1 * height - y) // 1800
    v2 = (0 - y) // 1800
    v3 = (-2 * height - y) // 1800
    return v0, v1, v2, v3

# 发球函数，总是做为West才发球
# ds为函数可以利用的存储字典
# 函数需要返回球的y坐标，和y方向的速度
def serve(ds:dict) -> tuple:
    return BALL_POS[1], ball_v_range(BALL_POS[1])[1] + 1

# 打球函数
# tb为TableData类型的对象
# ds为函数可以利用的存储字典
# 函数需要返回一个RacketAction对象
def play(tb:TableData, ds:dict) -> RacketAction:
    # 计算速度范围
    v_range = ball_v_range(tb.ball['velocity'].y)
    # 计算介于可行范围内的最小的目标v

    min_index = v_range.index(min(v_range, key=lambda x: abs(x - tb.ball['velocity'].y)))
    target = v_range[min_index] + 1 - 2 * (min_index % 2) - tb.ball['velocity'].y

    # 如果有道具，则对自己使用
    if tb.cards['cards']:
        side, item = 'SELF', tb.cards['cards'].pop(0)
    else:
        side, item = None, None
    # 返回
    return RacketAction(tb.tick, tb.ball['position'].y - tb.side['position'].y, target, 500000 - tb.ball['position'].y, side, item)

# 对局后保存历史数据函数
# ds为函数可以利用的存储字典
# 本函数在对局结束后调用，用于双方分析和保存历史数据
def summarize(tick:int, winner:str, reason:str, west:RacketData, east:RacketData, ball:BallData, ds:dict):
    return