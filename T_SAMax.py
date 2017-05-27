from table import *
from test import *
import time
import numpy as np
import pandas as pd

Height = 1000000
C = 0.67
# 固定的V指向区间，默认以V=0时为取余数点。分为两个数组
V_range1 = np.arange(-1999800, -1800, 1800)
V_range2 = np.arange(1000800, 2998800, 1800)
# Series共用，V_range to Series
Series1 = pd.Series(V_range1, index=V_range1)
Series2 = pd.Series(V_range2, index=V_range2)

Random = [np.random.random() for i in range(1000000)]
# 球的
Card_Value = {
    'SP': 500,
    'DS': 0,
    'IL': 2000,
    'DL': 2000,
    'TP': 1000,
    'AM': 1500,
}


# 返回真实点的高度
def y2real(y):
    # 关于np问题的过滤
    if type(y) is np.ndarray:
        y_real = np.where(y % (2 * Height) < Height, y % Height, Height - y % Height)
        return y_real
    if y % (2 * Height) < Height:
        y_real = y % Height
    else:
        y_real = Height - y % Height
    return y_real
    # n_mirror, remain = divmod(y, DIM[3])
    # # n_mirror是穿过墙的数目
    # return {0: remain, 1: DIM[3] - remain}[n_mirror % 2]


# 对手的估值函数
def op_player_f(v, v0, y0):
    """
    对手估值函数
    :param v: 打过去的速度
    :param v0: 接到时的速度
    :param y0: 接到的位置
    :return: 
    """
    lose = int(((v - v0) / FACTOR_SPEED) ** 2)
    op_lose = int(((y2real(y0 - 1800 * v0) - y2real(y0 + 1800 * v)) / FACTOR_DISTANCE) ** 2) * C

    return -(lose - op_lose)


def getMax(v0, y0, target_range=None, T_start=2000, gamma=0.99, T_end=2, evaluate=op_player_f):
    """
    求给定一元函数求v_range最大值。使用模拟退火算法
    :param target_range: 指向对面坐标可以取值的范围
    :param T_end: 
    :param gamma: 
    :param T_start: 
    :param v0: 
    :param y0: 
    :param evaluate: 
    :return: 
    """
    # 首先做v1
    if target_range == None:
        # 获取符合这个y0的v范围
        if v0 <= 0:
            target_range = V_range1 + y0 % 1800
        else:
            target_range = V_range2 + y0 % 1800
            if y0 % 1800 >= 1200:
                target_range = target_range[:-1]
    current_v = int(len(target_range) * np.random.random())
    current_value = evaluate((target_range[current_v] - y0) // 1800, v0, y0)
    # value_matrix = evaluate(target_range, v0, y0)
    # 添加BSF，制胜法宝
    BSF = current_v, current_value
    TTL = 50
    while T_start > T_end:
        # 获取下一个值：
        new_v = (int(T_start * (-0.5 + np.random.random())) + current_v) % len(target_range)
        # 获取新的估值
        new_value = evaluate((target_range[current_v] - y0) // 1800, v0, y0)
        dE = new_value - current_value
        # 获取随机
        ran = np.random.random()
        # 判断是否满足跃迁条件
        if dE > 0 or ran <= np.exp(-dE / T_start):
            current_v = new_v
            current_value = new_value
            BSF = max(BSF, (current_v, current_value), key=lambda x: x[1])
        # 降温
        T_start *= gamma
        # print(current_v, current_value, sep = ',')
    v_best = (target_range[BSF[0]] - y0) // 1800
    # print(v_best - v0, '*********************')
    return v_best, BSF[1]


def pandas_max(v0, y0, target_range=None):
    """
    pandas暴力求最值
    熊猫就是无敌
    :param v0: 
    :param y0: 
    :param target_range: 
    :return: 
    """
    if target_range is None:
        # 获取符合这个y0的v范围
        if v0 <= 0:
            target_range = Series1 + y0 % 1800
        else:
            target_range = Series2 + y0 % 1800
            # 排除最后一个值超标的情况
            if y0 % 1800 >= 1200:
                target_range = target_range[:-1]
        # 索引也同步增加
        target_range.index += y0 % 1800

    # print(np.nan in target_range)
    f = lambda v: op_player_f(v, v0, y0)
    values = target_range.apply(f)
    max_v = values.argmax()
    return (max_v - y0) // 1800, values[max_v]


# t1 = time.time()
# print(pandas_max(40,10000))
# t2 = time.time()
# print(t1,t2,t2-t1)



def serve(ds):
    return BALL_POS[1], (1800000 - BALL_POS[1]) // 1800 + 1


def play(tb: TableData, ds: dict) -> RacketAction:
    """
    主函数，每次游戏进程会调用这个函数
    :param tb: TableData，桌面数据情况。
    :param ds: dict，临时存储数据的字典
    :return: RacketAction，保存了这次的球拍移动的四项信息。
    """
    # return RacketAction(tb.tick, tb.ball['position'].y - tb.side['position'].y, 0, 0)
    # t1 = time.time()
    v0, y0 = tb.ball['velocity'].y, tb.ball['position'].y
    # 这里注释掉这句，是为了考虑是否取消启发式判断速度范围获取更大利益
    # v_best1 = pandas_max(v0, y0)[0]
    v_best = max((pandas_max(v0, y0, Series1), pandas_max(v0, y0, Series2)), key=lambda x: x[1])[0]
    # 如果有道具，则对自己使用
    if tb.cards['cards']:
        side, item = 'SELF', tb.cards['cards'].pop(0)
    else:
        side, item = None, None
    # t2 = time.time()
    # print(t1,t2,t2-t1)
    return RacketAction(tb.tick, tb.ball['position'].y - tb.side['position'].y,
                        int(v_best - tb.ball['velocity'].y),
                        (500000 - tb.ball['position'].y) // 2,
                        side, item)


def summarize(tick: int, winner: str, reason: str, west: RacketData, east: RacketData, ball: BallData, ds: dict):
    return


#
# import time
# a = time.time()
# print(getMax(455,16000))
# b=time.time()
# print(a,b,b-a)


def evaluate(bd, pd, opd):
    """
    
    :param bd: 
    :param pd: 
    :param opd: 
    :return: 
    """
