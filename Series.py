from table import *
import pandas as pd
import numpy as np
Height = 1000000
C = 0.67
Ct = 0.85
STEP = 1800

# 道具部分代码笔记：
# 1.获取时，路径上加一个数，使能获取道具的路径的估值更大
# 2.根据路径判断是否使用变压器、瞬移、旋转球，也即将道具对体力值的作用补充完整
# 3.不考虑隐身术，但是注意不要出BUG，应对好None
# 4.如果路径判断的道具没有使用，在RocketAction前加判断使用优先级最大的道具

def play(tb:TableData, ds) -> RacketAction:
    """
    主程序play，反复调用
    :param y0: int，打到我方底线时球的y轴坐标
    :param v0: int，打到我方底线时球的y轴速度
    :param p_v: Series，我方可能的出射速度
    :param y1: Series，打到对方底线时球的y轴坐标
    :param v1: Series，打到对方底线时球的y轴速度
    :param op_chosen_v: Series，对手最终决定的回球方式
    :param p_life1, op_life1: 对方上一轮迎球加速跑位加减血道具生效而我方尚未作出迎球反应时双方体力值
    :param p_life2, op_life2: 决策后双方体力值
    :param path_assume: Series，我方的估值函数值
    :return: RacketAction，我方最终决定的回球方式
    """
    # 创建ball_data元组
    b_d = (tb.ball['position'].x,tb.ball['position'].y,tb.ball['velocity'].x,tb.ball['velocity'].y,tb.tick)
    # 创建player_data（迎球方）和op_player_data（跑位方）元组
    p_d = (tb.side["life"], tb.side['position'].y)
    op_d = (tb.op_side["life"], tb.op_side["active_card"])
    # 创建cards元组
    cards = (tb.cards['card_tick'], tb.cards['cards'])
    ###################################################
    y0, v0 = b_d[1], b_d[3]
    # cards_available:桌面上现有的道具列表
    cards_available = cards[1]
    # 对方上一轮迎球加速跑位加减血道具生效而我方尚未作出迎球反应时双方体力值
    p_life1, op_life1= p_d[0], op_d[0]

    # TODO 改系数，获得合理的等距v的Series，会用到ball_v_range(b_d)
    p_v = pd.Series([1000 * i for i in range(50)])

    # y1为到达对方时球的y轴坐标，op_chosen_v为对方回球的y轴速度
    y1, op_chosen_v = op_play(y0, p_v)

    # 计算双方决策后的“体力值”
    # 对于我方而言，不等同于体力值，因为加入了获得道具的“加分”
    # 对对方而言，也不等同于体力值，因为是只考虑一小部分的体力估值
    p_life2, p_card_side, p_active_card = p_life_consume(b_d, p_d, op_d, cards_available, p_v, op_chosen_v, y1)
    op_life2 = op_life_consume(op_d, y0, op_chosen_v, y1, p_active_card)

    # 获得我方估值函数值中的最大值对应索引
    p_path_assume = (p_life2 - p_life1) - (op_life2 - op_life1)
    index = p_path_assume.argmax()

    # 返回具体打球方式
    p_chosen_v = p_v[index]
    p_chosen_side = p_card_side[index]
    p_chosen_card = p_active_card[index]
    return RacketAction(tb.tick, tb.ball['position'].y - tb.side['position'].y, p_chosen_v - v0, 0, p_chosen_side, p_chosen_card)

def p_life_consume(b_d, p_d, op_d, cards_available:list, p_v:pd.Series, op_chosen_v:pd.Series, y1:pd.Series):
    """
    根据我方此次决策，算出迎球+加速+跑位的总体力消耗(考虑道具)
    :param p_d: 决策前迎球方的信息
    :param op_d: 决策前跑位方的信息
    :param cards_available: list, 决策前桌面上可供获取的道具信息
    :param player_action: 我方此次决策结果 RocketAction类
    :param bat_distance: 此次决策指定迎球的距离
    :param run_distance: 此次决策指定跑位的距离
    :return: 执行完决策后我方体力值消耗
    """
    p_life = p_d[0]
    op_active_card = op_d[1]
    y0, v0 = b_d[1], b_d[3]
    # y2和v2是对方决策后在我方的落点以及我方的速度
    y2, v2 = ball_fly_to(y1, op_chosen_v)
    # 我方决策跑位到 对方决策后在我方的落点 与 当下位置的中点
    middle = (y2 + p_d[1])//2

    v_will_hit = ball_fly_to_card(b_d, cards_available)
    # 此函数在本页最后,萌萌哒叶老师还在写
    # TODO 这里要判断v_will_hit里包含的所有速度是否在p_v（如果不在我认为应该把相差最小的改为能击中道具的速度）
    # 这里是为了后面能将道具获取也纳入估值系统内（估值函数能显示出走这条能获得道具的路更有益）做铺垫


    # TODO 道具的具体使用
    # 这里和路径选取以及道具获取没有关系，这一步必然放在player_action赋值之前。
    # 选择依据是根据p_v以及op_chosen_v之类，先考虑旋转、变压、瞬移道具（如果有）的使用受益是否超过设定值，超过则用
    # 不超过则考虑加血减血包的使用（如果有）。以上使用内部还应该根据实际情况划出优先级。

    p_active_card = None
    p_card_side = None

    # 获取我方可能的决策结果
    player_action = RacketAction(b_d[4], y0 - p_d[1], p_v - v0, middle, p_card_side, p_active_card)

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
    # 按照跑位的距离减少体力值（考虑我方可能使用瞬移卡道具）
    param = 0
    if player_action.card[1] == CARD_TLPT:  # 如果碰到瞬移卡，则从距离减去CARD_TLPT_PARAM再计算体力值减少
        param = CARD_TLPT_PARAM
    if abs(run_distance) - param > 0:
        p_life -= (abs(run_distance) - param) ** 2 // FACTOR_DISTANCE ** 2
    # 考虑我方可能使用加血包道具
    if player_action.card[1] == CARD_INCL:
        p_life += CARD_INCL_PARAM

    # TODO 在最后，对击中不同的道具的p_v路径给予不同的p_life“加分”，以便估值函数能显示出走这条能获得道具的路更有益
    # 显然加血包减血包就应该是CARD_INCL_PARAM = 2000 CARD_DECL_PARAM = 2000，其他加分按照（可能的受益*下一轮使用概率）来计算

    # 返回执行决策后p_life,p_card_side和p_active_card
    return p_life, p_card_side, p_active_card

def op_life_consume(op_d, y0, op_chosen_v, y1, p_active_card):
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
    op_life = op_d[0]
    op_vy = op_chosen_v
    op_y = y1
    # 减少体力值（考虑我方可能使用掉血包道具）
    if p_active_card == CARD_DECL:
        op_life -= CARD_DECL_PARAM
    # 对方决策在我方处的落点
    y2, v2 = ball_fly_to(op_y, op_vy)
    # 对方跑位到我方落点与当下位置中某一点
    middle = Ct * (y2 - op_y) + op_y
    # 获取对方的决策结果
    op_player_action = RacketAction(7200, Ct * (y2 - y0) + y0 , op_vy - v2, middle, None, None)# 下文中tick没用，随便取一个合法值
    # 将迎球方动作中的距离速度等值规整化为整数
    op_player_action.normalize()
    # 球拍的全速是球X方向速度，按照体力值比例下降
    velocity = int((op_life / RACKET_LIFE) * BALL_V[1])
    # bat_distance 为指定迎球的距离
    bat_distance = op_player_action.bat

    # 如果指定迎球的距离大于最大速度的距离，则丢球，比赛结束
    if abs(bat_distance) > velocity * STEP:
        return False

    # 按照迎球的距离减少体力值（考虑我方可能使用变压器道具）
    op_life -= (abs(bat_distance) ** 2 // FACTOR_DISTANCE ** 2) * (CARD_AMPL_PARAM if p_active_card == CARD_AMPL else 1)
    # 按照给球加速度的指标减少体力值（考虑我方可能使用变压器道具）
    op_life -= (abs(op_player_action.acc) ** 2 // FACTOR_SPEED ** 2) * (CARD_AMPL_PARAM if p_active_card == CARD_AMPL else 1)

    # 如果指定跑位的距离大于最大速度的距离，则采用最大速度距离
    run_distance = sign(op_player_action.run) * min(abs(op_player_action.run), velocity * STEP)
    '''    
    # 按照跑位的距离减少体力值（考虑对方可能使用瞬移卡道具）
    param = 0
    if op_player_action.card[1] == CARD_TLPT:  # 如果碰到瞬移卡，则从距离减去CARD_TLPT_PARAM再计算体力值减少
        param = CARD_TLPT_PARAM
    if abs(run_distance) - param > 0:
        op_life -= (abs(run_distance) - param) ** 2 // FACTOR_DISTANCE ** 2
    # 考虑对方可能使用加血包道具
    if op_player_action.card[1] == CARD_INCL:
        op_life += CARD_INCL_PARAM
    '''
    # 按照跑位的距离减少体力值（听说对方不用道具，上方判断无用）
    op_life -= abs(run_distance) ** 2 // FACTOR_DISTANCE ** 2
    # 返回执行决策后op_life
    return op_life


def op_play(y0:int, p_v:pd.Series):
    """
    对手play
    :param y0: int，我方出射点坐标
    :param p_v: Series，我方选择的一系列出射速度
    :param y1: Series，打到对手底线时球的y轴坐标
    :param v1: Series，打到对手底线时球的y轴速度
    :param op_chosen_v: Series，对手最终决定的回球方式
    :return: Series，对手最终决定的回球方式
    """
    y1, v1 = ball_fly_to(y0, p_v)
    op_chosen_v = op_choose(y1, v1, y0)
    return y1, op_chosen_v

def op_choose(y1:pd.Series, v1:pd.Series, y0:int):
    # TODO 这里Series运算好像有很多不规范...应该是要改掉运算表示
    """
    面对(y1,v1)，对手的选择
    :param y1: int，打到对手底线时球的y轴坐标
    :param v1: int，打到对手底线时球的y轴速度
    :param op_v: Series，对手可能的回球方式
    :param op_assume: Series，对手可能的回球方式的估值函数值
    :return: int，对手最终决定的回球方式
    """
    # TODO 改系数，获得合理的等距v的Series
    op_v = pd.Series([1000 * i for i in range(5)])
    op_assume = op_assume_f(op_v, y1, v1, y0)
    op_chosen_v = op_v[op_assume.argmax()]
    return op_chosen_v

def op_assume_f(op_v:pd.Series, y1:pd.Series, v1:pd.Series, y0:int):
    # TODO 这里Series运算好像有很多不规范...应该是要改掉运算表示
    # 我始终觉得我们似不似把对手想的太傻了...这个算法我没仔细看，可能有不恰当
    """
    只会想一层的可爱对手使用的估值函数
    对方只考虑我方为接此球移动消耗体力与每次击球所消耗体力的差值最大
    :param op_v: Series，对手回击后球的速度
    :param v1: Series，打到对方底线时球的y轴速度
    :param y1: Series，打到对方底线时球的y轴坐标
    :param y2: Series，打到我方底线时球的y轴坐标
    :return: Series，估值函数值（我方为接此球移动消耗体力与每次击球所消耗体力的差值）
    """
    # 对方将球从v1加速至op_v所消耗体力
    op_lose = int(((op_v - v1)/FACTOR_SPEED)**2)
    # 我方将从y0跑位至y0和y2之间的某一点，并到y2处迎球
    y2 = mirror2real(y1 + 1800 * op_v)[0]
    # C为可调试的常数，取值范围0.5-1，
    p_lose = int(C * ((y0 - y2)/FACTOR_DISTANCE)**2)
    return p_lose - op_lose

def ball_fly_to(y0:int, p_v:pd.Series):
    # TODO 这里Series运算好像有很多不规范...应该是要改掉运算表示
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

def mirror2real(Y:pd.Series):
    # TODO 这里Series运算好像有很多不规范...应该是要改掉运算表示
    """
    将镜像点映射为真实点
    :param y: 镜像点y坐标
    :param y_real: 真实点y坐标
    :return: 真实点y坐标数组（范围0-1,000,000），碰撞次数数组
    """
    if type(Y) is pd.Series:
        y_real = pd.Series.where( Y % (2 * Height) < Height, Y % Height, 2 * Height - Y % Height)
        if Y % Height != 0:  # 若球没有打在边界上
            count = Y // Height
        else:  # 若恰好在边界上
            count = (Y // Height if (Y > 0) else (1 - Y // Height))
        return y_real, count

def ball_fly_to_card(b_d:tuple, cards_al:list):
    """
    cards_al means cards_available
    根据桌面上现有的道具种类以及位置和球所在的位置，计算对应的各个道具的竖直速度
    :param b_d:  b_d = (tb.ball['position'].x,tb.ball['position'].y,tb.ball['velocity'].x,tb.ball['velocity'].y,tb.tick)
    :param cards_al: list，决策前桌面上道具的信息，元素是Card类
    :return: 返回一个list，元素为符合击中某道具要求的竖直速度。注意！要求索引对应cards_al里面的道具或者其他简洁方式可以获知对应关系
    """
    pass


def ball_v_range(b_d):
    """
    根据我方出射点坐标，算出y轴可取速度的边界值
    :param bd: (tb.ball['position'].x,tb.ball['position'].y,tb.ball['velocity'].x,tb.ball['velocity'].y)
    :param tb.step: 1800 tick
    :param Y: 镜像点y坐标
    :return: 与桌碰撞次数  
    """
    y0 = b_d[1]
    # v0,v1,v2,v3是速度的范围边界:可取[v3,v2]∪[v1,v0]
    v0 = (3 * Height - y0) // STEP
    v1 = (1 * Height - y0) // STEP + 1
    v2 = (0 - y0) // STEP
    v3 = (-2 * Height - y0) // STEP + 1
    # 贴边打的情况算作反弹零次，需要排除
    if y0 == 0:
        v2 = -1
    return v0, v1, v2, v3