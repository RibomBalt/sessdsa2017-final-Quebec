from table import *
from test import *
import numpy as np

Height = 1000000
C = 0.67
# 固定的V指向区间，默认以V=0时为取余数点。分为两个数组，符合test.py里的速度范围
V_range = np.array([*np.arange(-1999800, -1800, 1800),*np.arange(1000800, 2998800, 1800)])
Random = [np.random.random() for i in range(1000000)]

#返回真实点的高度
def y2real(y):
    """
    将镜像点映射为真实点
    :param y: 镜像点y坐标
    :param y_real: 真实点y坐标
    :return: 真实点y坐标，范围0-1,000,000
    """
    # 关于np问题的过滤
    if type(y) is np.ndarray:
        y_real = np.where(y % (2*Height) < Height, y % Height, 2*Height - y % Height)
        return y_real
    '''
    # 原代码
    if y % (2*Height) < Height:
        y_real = y % Height
    else:
        y_real = 2 * Height - y % Height
    '''
    # 修改后
    n_mirror, remain = divmod(y, Height)
    # n_mirror是穿过墙的数目，可正可负
    y_real = {0: remain, 1: Height - remain}[n_mirror % 2]
    return y_real

#估值函数
def op_assume(v,v0,y0):
    """
    估值函数
    :param v: 打过去的速度
    :param v0: 接到时的速度
    :param y0: 接到的位置
    :return: 
    """
    p_lose = int(((v - v0)/FACTOR_SPEED)**2)
    op_lose = int(((y2real(y0 - 1800*v0) - C * y2real(y0 + 1800*v))/FACTOR_DISTANCE)**2)
    return p_lose - op_lose


def getMax(v0, y0, target_range = None, T_start = 1000, gamma = 0.99, T_end = 20, evaluate = op_player_f):
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
        target_range = V_range + y0 % 1800
    current_v = int(len(V_range) * np.random.random())
    current_value = evaluate((target_range[current_v]-y0)//1800, v0, y0)
    # value_matrix = evaluate(target_range, v0, y0)
    # 添加BSF，制胜法宝
    BSF = current_v, current_value
    TTL = 50
    while T_start > T_end:
        # 获取下一个值：
        new_v = (int(T_start * (-0.5 + np.random.random())) + current_v) % len(target_range)
        # 获取新的估值
        new_value = evaluate((target_range[current_v]-y0)//1800, v0, y0)
        dE = new_value - current_value
        # 获取随机
        ran = np.random.random()
        # 判断是否满足跃迁条件
        if dE > 0 or ran <= np.exp(-dE/T_start):
            current_v = new_v
            current_value = new_value
            BSF = max(BSF, (current_v, current_value), key = lambda x:x[1])
        # 降温
        T_start *= gamma
        # print(current_v, current_value, sep = ',')
    v_best = (target_range[BSF[0]] - y0) // 1800
    # print(v_best)
    return v_best, BSF[1]


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
    v0, y0 = tb.ball['velocity'].y, tb.ball['position'].y
    v_best = getMax(v0, y0)[0]
    return RacketAction(tb.tick, tb.ball['position'].y - tb.side['position'].y,
                        int(v_best-tb.ball['velocity'].y),
                        (500000 - tb.ball['position'].y)//2,
                        None,None)

def summarize(tick:int, winner:str, reason:str, west:RacketData, east:RacketData, ball:BallData, ds:dict):
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