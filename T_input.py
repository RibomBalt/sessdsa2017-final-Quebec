from table import *


# tb为TableData类型的对象
# ds为函数可以利用的存储字典
# 函数需要返回一个RacketAction对象

def yspeed2mirror(y_speed: int, o_axis: int):
    """
    将镜像点映射为真实点
    :param y_speed: y向速度
    :param o_axis: 发球点的y坐标，原点、镜点均可
    :return: 返回打到的镜点
    """
    # 目前没有更加方便借鉴的常数
    return o_axis + y_speed * 3600


def mirror2real(y_axis: int):
    """
    将镜像点映射为真实点
    :param o_axis: 原点的真实y坐标（一般代发球点的真实y坐标）
    :param y_axis: 镜像点y坐标
    :return: 真实点y坐标，范围0-1,000,000
    """
    n_mirror, remain = divmod(y_axis, DIM[3])
    # n_mirror是穿过墙的数目
    return {0: remain, 1: DIM[3] - remain}[n_mirror % 2]


def ball_v_range(tb: TableData, ticks: int = 3600):
    """
    得到可以打到的速度范围
    :param tb: TableData
    :param ticks: 一次经过的时间
    :return: 
    """
    # v0,v1,v2,v3是速度的范围边界
    v0 = (3 * tb.ball.extent[3] - tb.ball.pos.y) // ticks
    v1 = (1 * tb.ball.extent[3] - tb.ball.pos.y) // ticks
    v2 = (0 - tb.ball.pos.y) // ticks
    v3 = (-2 * tb.ball.extent[3] - tb.ball.pos.y) // ticks
    return v0, v1, v2, v3


def serve(ds):
    return BALL_POS[1], BALL_V[1]


def play(tb: TableData, ds: dict) -> RacketAction:
    """
    主函数，每次游戏进程会调用这个函数
    :param tb: TableData，桌面数据情况。
    :param ds: dict，临时存储数据的字典
    :return: RacketAction，保存了这次的球拍移动的四项信息。
    """
    # return RacketAction(tb.tick, tb.ball['position'].y - tb.side['position'].y, 0, 0)
    d = {'y_speed':0, 'y_go':0}
    def print_stack():
        print('tick:', tb.tick)
        print('step:', tb.step)
        print('side:', tb.side)
        print('op_side:', tb.op_side)
        print('ball:', tb.ball)
        print('cards:', tb.cards)
    while True:
        s = input()
        if s == 'p':
            print_stack()
        elif s == 'q':
            break
        else:
            l = s.split()
            d[l[0]] = int(l[1])
    return RacketAction(tb.tick, tb.ball['position'].y - tb.side['position'].y,
                        d['y_speed'], d['y_go'], None, None)

def summarize(tick:int, winner:str, reason:str, west:RacketData, east:RacketData, ball:BallData, ds:dict):
    return