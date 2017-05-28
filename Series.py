from table import *
import pandas as pd
import numpy as np
Height = 1000000
C = 0.67
STEP = 1800
# 1.获取时，路径上加一个数，使能获取道具的路径的估值更大
# 2.根据路径判断是否使用变压器、瞬移、旋转球
# 3.不考虑隐身术，但是注意不要出BUG，应对好None
# 4.如果路径判断的道具没有使用，在RocketAction前加判断使用优先级最大的道具

'''
class RacketAction_Series:  # 球拍动作
    def __init__(self, tick, bat_vector, acc_vector, run_vector, side, card):
        # self.t0 = tick  # tick时刻的动作，都是一维矢量，仅在y轴方向
        self.bat = bat_vector  # t0~t1迎球的动作矢量（移动方向及距离）
        self.acc = acc_vector  # t1触球加速矢量（加速的方向及速度）
        self.run = run_vector  # t1~t2跑位的动作矢量（移动方向及距离）
        self.card = (side, card)  # 对'SELF'/'OPNT'使用道具
    def normalize(self):
        # 全都规范为整数
        self.bat = int(self.bat)
        self.acc = int(self.acc)
        self.run = int(self.run)
'''

# 首先先考虑对方如何回我们打出的一系列(v,y0)
# 只有v是变量

def play(tb:TableData, ds) -> RacketAction:
    """
    主程序play，反复调用
    :param y0: int，我方出射点坐标
    :param v0: int，我方出射点坐标
    :param p_v: Series，我方可能的出射速度
    :param y1: Series，打到对手底线时球的y轴坐标
    :param v1: Series，打到对手底线时球的y轴速度
    :param op_chosen_v: Series，对手最终决定的回球方式
    :return: RacketAction，我方最终决定的回球方式
    """
    # 创建ball_data元组
    b_d = (tb.ball['position'].x,tb.ball['position'].y,tb.ball['velocity'].x,tb.ball['velocity'].y,tb.tick)
    # 创建player_data（迎球方）和op_player_data（跑位方）元组
    p_d = (tb.side["life"], tb.side['position'].y)
    op_d = (tb.op_side["life"], tb.op_side["active_card"])

    ##########然后下面只调用tb,ds,bd,pd,opd############
    y0, v0 = b_d[1], b_d[3]
    p_v = pd.Series([1000 * i for i in range(50)])
    op_chosen_v = op_play(y0, p_v)
    p_life_consume = life_consume(p_d, op_d, op_chosen_v)
    p_chosen_v =
    return RacketAction(tb.tick, tb.ball['position'].y - tb.side['position'].y, p_chosen_v - b_d, 0, None, None)

def life_consume(b_d, p_d, op_d, op_chosen_v):
    """
    根据我方此次决策，算出迎球+加速+跑位的总体力消耗(考虑道具)
    :param player_data: 决策前迎球方的信息
    :param op_player_data: 决策前跑位方的信息
    :param player_action: 我方此次决策结果 RocketAction类
    :param bat_distance: 此次决策指定迎球的距离
    :param run_distance: 此次决策指定跑位的距离
    :param p_d = (tb.side["life"])
    :param op_d = (tb.op_side["life"], tb.op_side["active_card"])
    :return: 执行完决策后我方体力值
    """
    p_life = p_d[0]
    op_active_card = op_d[1]

    # 减少体力值（考虑跑位方可能使用掉血包道具）
    if op_active_card == CARD_DECL:
        p_life -= CARD_DECL_PARAM

    # 获取我方可能的决策结果
    player_action = RacketAction(b_d[4], b_d[1] - p_d[1], p_v - b_d[3], 0, None, None)# TODO 跑位如何跑？道具如何用？
    '''
    player_action的属性： 
    .bat t0~t1迎球的动作矢量（移动方向及距离）
    .acc t1触球加速矢量（加速的方向及速度）
    .run t1~t2跑位的动作矢量（移动方向及距离）
    .card 对'SELF'/'OPNT'使用道具元组（(side, card)使用对象及道具）
    '''
    # 将迎球方动作中的距离速度等值规整化为整数
    player_action.normalize()
    # 球拍的全速是球X方向速度，按照体力值比例下降
    velocity = int((p_life / RACKET_LIFE) * BALL_V[1])
    # bat_distance 为指定迎球的距离
    bat_distance = player_action.bat
    # 如果指定迎球的距离大于最大速度的距离，则丢球，比赛结束
    if abs(bat_distance) > velocity * STEP:
        return False

    # 按照迎球的距离减少体力值（考虑对方之前可能使用变压器道具）
    p_life -= (abs(bat_distance) ** 2 // FACTOR_DISTANCE ** 2) * (CARD_AMPL_PARAM if op_active_card == CARD_AMPL else 1)
    # 按照给球加速度的指标减少体力值（考虑对方之前可能使用变压器道具）
    p_life -= (abs(player_action.acc) ** 2 // FACTOR_SPEED ** 2) * (CARD_AMPL_PARAM if op_active_card == CARD_AMPL else 1)

    # 如果指定跑位的距离大于最大速度的距离，则采用最大速度距离
    run_distance = sign(player_action.run) * min(abs(player_action.run), velocity * STEP)
    # 按照跑位的距离减少体力值（考虑对方之前可能使用瞬移卡道具）
    param = 0
    if player_action == CARD_TLPT:  # 如果碰到瞬移卡，则从距离减去CARD_TLPT_PARAM再计算体力值减少
        param = CARD_TLPT_PARAM
    if abs(run_distance) - param > 0:
        p_life -= (abs(run_distance) - param) ** 2 // FACTOR_DISTANCE ** 2
    # 考虑我方之前可能使用瞬移卡道具
    if player_action.card[1] == CARD_INCL:
        p_life += CARD_INCL_PARAM
    return p_life

def op_play(y0, p_v):
    """
    对手play，假装对手只会想一层
    :param y0: int，我方出射点坐标
    :param p_v: Series，我方选择的出射速度
    :param y1: Series，打到对手底线时球的y轴坐标
    :param v1: Series，打到对手底线时球的y轴速度
    :param op_chosen_v: Serries，对手最终决定的回球方式
    :return: Series，对手最终决定的回球方式
    """
    y1, v1 = ball_fly_to(y0, p_v)
    op_chosen_v = op_choose(y1, v1)
    return op_chosen_v

def op_choose(y1:int, v1:int):
    """
    面对(y1,v1)，对手的选择
    :param y1: int，打到对手底线时球的y轴坐标
    :param v1: int，打到对手底线时球的y轴速度
    :param op_v: Series，对手可能的回球方式
    :param op_assume: Series，对手可能的回球方式的估值函数值
    :return: int，对手最终决定的回球方式
    """
    op_v = pd.Series([1000 * i for i in range(5)])
    op_assume = op_assume_f(op_v, v1, y1)
    op_chosen_v = op_v[op_assume.argmax()]
    return op_chosen_v

def op_assume_f(v,v1:int,y1:int):
    """
    只会想一层的可爱对手使用的估值函数
    :param v: Series，对手回击后球的速度
    :param v1: int，打到对手底线时球的y轴速度
    :param y1: int，打到对手底线时球的y轴坐标
    :return: Series，估值函数值数组
    """
    p_lose = int(((v - v1)/FACTOR_SPEED)**2) # TODO 这个int()可能是错误的！
    op_lose = int(((mirror2real(y1 - 1800 * v1)[0] - C * mirror2real(y1 + 1800 * v))[0] / FACTOR_DISTANCE)**2)
    return p_lose - op_lose

def ball_fly_to(y0:int, p_v:pd.Series):
    """
    根据出射点坐标、出射速度，算出到达对侧位置速度
    :param y0: 出射点坐标
    :param p_v: Series，出射速度
    :param Y: Series，镜像点y坐标
    :param count: 与桌碰撞次数，可正可负
    :return: 到达对侧位置位置、速度
    """
    # Y 为没有墙壁时乒乓球到达的位置（镜像点）
    Y = y0 + p_v * STEP
    # 把镜像点转化为真实点
    y1 = mirror2real(Y)[0]
    # 计算并更新y轴速度
    count = mirror2real(Y)[1]
    v1 = p_v * ((count + 1) % 2 * 2 - 1)
    return y1, v1

def mirror2real(Y):
    """
    将镜像点映射为真实点
    :param y: 镜像点y坐标
    :param y_real: 真实点y坐标
    :return: 真实点y坐标数组（范围0-1,000,000），碰撞次数数组
    """
    if type(Y) is pd.Series:
        y_real = pd.Series.where( Y % (2 * Height) < Height, Y % Height, 2 * Height - Y % Height)
        count = # TODO 这里应该是一个碰撞次数的Series！
        return y_real, count

