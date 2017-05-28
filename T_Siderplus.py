from table import *
from test import *
import time
import numpy as np
import pandas as pd

# 发球函数，总是做为West才发球
# ds为函数可以利用的存储字典
# 函数需要返回球的y坐标，和y方向的速度
def serve(ds:dict) -> tuple:
    return BALL_POS[1], - 500000// 1800 - 1

# 打球函数
# tb为TableData类型的对象
# ds为函数可以利用的存储字典
# 函数需要返回一个RacketAction对象
Height = 1000000
C = 0.69
# 固定的V指向区间，默认以V=0时为取余数点。分为两个数组
V_range1 = np.arange(-1999800, -1800, 3600)
V_range2 = np.arange(1000800, 2998800, 3600)
# Series共用，V_range to Series
Series1 = pd.Series(V_range1, index=V_range1)
Series2 = pd.Series(V_range2, index=V_range2)

series = pd.concat([Series1, Series2])

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


def ball_fly(v, y0):
    """
    一次球飞过去，算出球的落点和速度
    :param v: 球飞出的速度
    :param y0: 球飞出的位置
    :return: 速度，位置
    """
    # 对数字运算

    y = y0 + 1800 * v
    if type(v) == np.ndarray:
        y_real = np.where(y % (2 * Height) < Height, y % Height, Height - y % Height)
        new_v = np.where(y % (2 * Height) < Height, v, -v)
        return y_real, new_v
    if y % (2 * Height) < Height:
        y_real = y % Height
    else:
        y_real = Height - y % Height
        v = -v
    return v, y_real


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


def pandas_max(v0, y0, target_range=None, evaluate=op_player_f):
    """
    pandas暴力求最值
    熊猫就是无敌
    :param v0:
    :param y0:
    :param target_range:
    :return: 对方返回的速度、相应估值
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
    if evaluate is op_player_f:
        f = lambda v: evaluate(v, v0, y0)
    else:
        f = evaluate
    values = target_range.apply(f)
    max_v = values.argmax()
    return (max_v - y0) // 1800, values[max_v]


# t1 = time.time()
# print(pandas_max(40,10000))
# t2 = time.time()
# print(t1,t2,t2-t1)

def player_f(v, v0, y0):
    """
    我方估值函数。算两层
    :param v:
    :param v0:
    :param y0:
    :return:
    """
    # 对方发球位置
    y1 = y2real(y0 - 1800 * v0)
    # 我们打到的位置
    v_in, y2 = ball_fly(v, y0)
    # 对方打回的速度
    # TODO 用对方函数算一个最小值出来，修改op_player_f估值为负
    if v0 < 0:
        vy = -1 - y0 / 1800 + v0
    else:
        vy = 557 - y0 / 1800 + v0
    v_out = vy
    # 打回的位置
    y3 = y2real(y2 + 1800 * v_out)
    # 己方决策函数
    # 知道自己的跑位，因此这一项赋给0.5
    lose = ((v - v0) / FACTOR_SPEED) ** 2 + 0.5 * ((y0 - y3) / FACTOR_DISTANCE) ** 2  # 己方损失
    op_lose = ((v_out - v_in) / FACTOR_SPEED) ** 2 + C * ((y1 - y2) / FACTOR_DISTANCE) ** 2  # 对方损失
    # 返回对方减少 - 我方减少。这个尽可能大
    return v, op_lose - lose, y3

def ball_v_range_up(bd:ball_data):
    """
    根据我方出射点坐标，算出y轴可取速度的边界值
    :param tb.step: 1800 tick
    :param Y: 镜像点y坐标
    :param height: 乒乓球桌的宽度, DIM[3] - DIM[2]
    :return: 与桌碰撞次数
    """
    #delta_height = 300
    v0 = (1 * Height - bd.pos_y) // STEP + 1
    v1 = (3 * Height - bd.pos_y) // STEP - 10
    v2 = (-1 * Height - bd.pos_y) // STEP + 1
    return v0, v1, v2

def ball_v_range_down(bd:ball_data):
    """
    根据我方出射点坐标，算出y轴可取速度的边界值
    :param tb.step: 1800 tick
    :param Y: 镜像点y坐标
    :param height: 乒乓球桌的宽度, DIM[3] - DIM[2]
    :return: 与桌碰撞次数
    """
    #delta_height = 300
    v0 = (-2* Height - bd.pos_y) // STEP + 1
    v1 = (2 * Height - bd.pos_y) // STEP + 1
    v2 = (- bd.pos_y) // STEP - 1
    return v0, v1, v2

def play(tb:TableData, ds:dict) -> RacketAction:
    times = tb.tick/1800
    bd = ball_data(tb)
    pd = player_data(tb)
    opd = op_player_data(tb)

    v0, y0 = tb.ball['velocity'].y, tb.ball['position'].y

    v_best = max((pandas_max(v0, y0, Series1, lambda v: player_f(v, v0, y0)[1]),
                  pandas_max(v0, y0, Series2, lambda v: player_f(v, v0, y0)[1])), key=lambda x: x[1])[0]
    y2reach = player_f(v_best, v0, y0)[2]
    # 如果有道具，则对自己使用
    if tb.cards['cards']:
        side, item = 'SELF', tb.cards['cards'].pop(0)
    else:
        side, item = None, None
        #计算速度范围
    #t = random.randint(0,1)
    if times%4 in (1,2):
        v_range = ball_v_range_up(bd)
    else:
        v_range = ball_v_range_down(bd)
    # 计算介于可行范围内的最小的目标v

    min_index = v_range.index(min(v_range, key=lambda x: abs(x - tb.ball['velocity'].y)))
    # 是大值则-1，小值则+1
    target = v_range[min_index] + 1 - tb.ball['velocity'].y

    # 如果有道具，则对自己使用
    if tb.cards['cards']:
        side, item = 'SELF', tb.cards['cards'].pop(0)
    else:
        side, item = None, None
    # 返回
    return RacketAction(tb.tick, tb.ball['position'].y - tb.side['position'].y,
                        target, (y2reach - tb.ball['position'].y)//2, side, item)

# 对局后保存历史数据函数
# ds为函数可以利用的存储字典
# 本函数在对局结束后调用，用于双方分析和保存历史数据
def summarize(tick:int, winner:str, reason:str, west:RacketData, east:RacketData, ball:BallData, ds:dict):
    return