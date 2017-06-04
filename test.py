# 从table中导入所有常量
from table import *
# STEP 半个来回时长
STEP = 1800
"""
修改内容：
1.完善了速度取值的边界
2.撞墙的判定可以用杨帆的函数，更加简洁
3.目前没有加血包和减血包的情况
"""

'''
# 打球函数
def play(tb:TableData, ds) -> RacketAction:
    # 创建ball_data类实例
    bd = ball_data(tb)
    # 创建player_data类（迎球方）和op_player_data类（跑位方）实例
    pd = player_data(tb)
    opd = op_player_data(tb)
    ##########然后调用下面的函数，传入tb,ds,bd,pd,opd############
    return RacketAction(tb.tick, tb.ball['position'].y - tb.side['position'].y, 0, 0, None, None)
'''

# 假装打球函数
def pretend_play(tb:TableData, ds) -> RacketAction:
    return RacketAction(tb.tick, tb.ball['position'].y - tb.side['position'].y, 0, 0, None, None)

class ball_data():
    def __init__(self, tb):
        self.pos_x = tb.ball['position'].x
        self.pos_y = tb.ball['position'].y
        self.vel_x = tb.ball['velocity'].x
        self.vel_y = tb.ball['velocity'].y

class player_data():
    def __init__(self, tb):
        self.life = tb.side["life"]

class op_player_data():
    def __init__(self, tb):
        self.active_card = tb.op_side["active_card"]

'''
# 这是原始的fly函数
def ball_fly_to(bd:ball_data):
    """
    根据我方出射点坐标、出射速度，算出到达对方位置
    :param tb.step: 1800 tick
    :param Y: 镜像点y坐标
    :param count: 与桌碰撞次数
    :param height: 乒乓球桌的宽度, DIM[3] - DIM[2]
    :return: 与桌碰撞次数
    """
    # x方向的位置更新
    # tb.step 为 1800 tick
    bd.pos_x += bd.vel_x * STEP
    # Y 为 没有墙壁时乒乓球到达的位置
    Y = bd.vel_y * STEP + bd.pos_y
    height = DIM[3] - DIM[2]
    # 若球没有打在边界上(以下计算过程具体解释详见 table.py Ball类的fly()函数)
    if Y % height != 0:
        # 计算碰撞次数
        count = Y // height
        # 计算真实点y轴坐标
        bd.pos_y = (Y - count * height * (1 - 2 * (count % 2)) + height * (count % 2))
    # 若恰好在边界上
    else:
        # 计算碰撞次数
        count = (Y // height if (Y > 0) else (1 - Y // height))
        # 计算真实点y轴坐标
        bd.pos_y = Y % (2 * height)
    # 计算并更新y轴速度
    bd.vel_y = bd.vel_y * ((count + 1) % 2 * 2 - 1)
    return abs(count), bd
'''

def ball_fly_to(bd:ball_data):
    """
    根据我方出射点坐标、出射速度，算出到达对方位置
    :param tb.step: 1800 tick
    :param Y: 镜像点y坐标
    :param count: 与桌碰撞次数，可正可负
    :param height: 乒乓球桌的宽度, DIM[3] - DIM[2]
    :return: 与桌碰撞次数
    """
    # x方向的位置更新
    # tb.step 为 1800 tick
    bd.pos_x += bd.vel_x * STEP
    # Y 为没有墙壁时乒乓球到达的位置（镜像点）
    Y = bd.vel_y * STEP + bd.pos_y
    # 把镜像点转化为真实点
    bd.pos_y = mirror2real(Y)[0]
    # 计算并更新y轴速度
    count = mirror2real(Y)[1]
    bd.vel_y = bd.vel_y * ((count + 1) % 2 * 2 - 1)
    return bd, abs(count)

def mirror2real(y_axis:int):
    """
    将镜像点映射为真实点
    :param y_axis: 镜像点y坐标
    :return: 真实点y坐标，范围0-1,000,000
    """
    n_mirror, remain = divmod(y_axis, DIM[3] - DIM[2])
    # n_mirror是穿过墙的数目，可正可负
    return {0:remain, 1:DIM[3] - remain}[n_mirror % 2], n_mirror

def side_life_consume(pd:player_data, opd:op_player_data, tb:TableData, ds):
    """
    根据我方此次决策，算出迎球+加速+跑位的总体力消耗(考虑道具)
    :param player_data: 决策前迎球方的信息
    :param op_player_data: 决策前跑位方的信息
    :param player_action: 我方此次决策结果 RocketAction类
    :param bat_distance: 此次决策指定迎球的距离
    :param run_distance: 此次决策指定跑位的距离
    :return: 执行完决策后我方体力值
    """
    # 减少体力值（考虑跑位方可能使用掉血包道具）
    if opd.active_card == CARD_DECL:
        pd.life -= CARD_DECL_PARAM
    # 获取我方此次决策结果
    player_action = pretend_play(tb, ds)
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
    velocity = int((pd.life / RACKET_LIFE) * BALL_V[1])
    # bat_distance 为指定迎球的距离
    bat_distance = player_action.bat
    # 如果指定迎球的距离大于最大速度的距离，则丢球，比赛结束
    if abs(bat_distance) > velocity * tb.step:
        return False

    # 按照迎球的距离减少体力值（考虑跑位方之前可能使用变压器道具）
    pd.life -= (abs(bat_distance) ** 2 // FACTOR_DISTANCE ** 2) * (CARD_AMPL_PARAM if opd.active_card == CARD_AMPL else 1)

    # 按照给球加速度的指标减少体力值（考虑跑位方之前可能使用变压器道具）
    pd.life -= (abs(player_action.acc) ** 2 // FACTOR_SPEED ** 2) * (CARD_AMPL_PARAM if opd.active_card == CARD_AMPL else 1)

    # 如果指定跑位的距离大于最大速度的距离，则采用最大速度距离
    run_distance = sign(player_action.run) * min(abs(player_action.run), velocity * tb.step)

    # 按照跑位的距离减少体力值（考虑跑位方之前可能使用变压器道具）
    param = 0
    if player_action == CARD_TLPT:  # 如果碰到瞬移卡，则从距离减去CARD_TLPT_PARAM再计算体力值减少
        param = CARD_TLPT_PARAM
    if abs(run_distance) - param > 0:
        pd.life -= (abs(run_distance) - param) ** 2 // FACTOR_DISTANCE ** 2
    return pd.life

'''
def get_op_acc(bd:ball_data):
    """
    根据对方打过来的球的速度位置，反推出跑位方（对方）加速度
    :param height: 乒乓球桌的宽度, DIM[3] - DIM[2]
    :param count: 与桌碰撞次数
    :return: 跑位方（对方）加速度
    """
    # Y 为 没有墙壁时到达的位置
    Y = -bd.vel_y * STEP + bd.pos_y
    height = DIM[3] - DIM[2]
    # 若球没有打在边界上，计算碰撞次数
    if Y % height != 0:
        count = Y // height
    else:# 若恰好在边界上
        count = (Y // height if (Y > 0) else (1 - Y // height))
    return bd.vel_y * ((count + 1) % 2 * 2 - 1) - 111
    # 此次111本应该为我方上一次打球至对方处，球y轴的速度。此数据应当从pingpong.py里29行左右（记录日志项）log中获取。
    # 暂时搁置
'''
# 5.29修改，一共改动了三个函数
def ball_v_range(b_d:tuple) -> tuple:
    """
    根据我方出射点坐标，算出y轴可取速度的边界值
    :param STEP: 1800 tick
    :param b_d[2]: b_d[2] = tb.ball['position'].y,接球时球的纵坐标
    :param height: 乒乓球桌的宽度, DIM[3] - DIM[2]
    :return: 可取速度的边界
    """
    height = DIM[3] - DIM[2]
    # v0,v1,v2,v3是速度的范围边界:可取[v3,v2]∪[v1,v0]
    v0 = (3 * height - b_d[2]) // STEP
    v1 = (1 * height - b_d[2]) // STEP + 1
    v2 = (0 - b_d[2]) // STEP
    v3 = (-2 * height - b_d[2]) // STEP + 1
    # 贴边打的情况算作反弹零次，需要排除
    if v2 == 0:
        v2 = -1
    # 返回一个元组，依次为速度的四个边界值
    return v0, v1, v2, v3

def fly_assistant(b_d:tuple, v_range:tuple, card:Card) -> list:
    """
    根据某个确定的道具位置和球所在的位置，计算吃到它所需要的竖直速度
    :param b_d: b_d = (tb.ball['position'].x,tb.ball['position'].y,tb.ball['velocity'].x,tb.ball['velocity'].y,tb.tick)
    :param v_range: 满足规则（碰撞1-2次）的速度区间[v3,v2]∪[v1,v0]
    :param card: 是一个Card类
    :param height: 球桌宽度，DIM[3] - DIM[2]
    :param x0: x0 = b_d[0]，接球时球的横坐标
    :param y0: y0 = b_d[1]，接球时球的纵坐标
    :param vx0: vx0 = b_d[2]，球的水平速度
    :return: 返回一个list，元素为符合击中某道具要求的竖直速度
    """
    height = DIM[3] - DIM[2]
    x0, y0, vx0 = b_d[0], b_d[1], b_d[2]
    # 满足规则（碰撞1-2次）的速度区间[v3,v2]∪[v1,v0]
    v0, v1, v2, v3 = v_range
    # 要吃的道具共有五个可能的镜像点/真实点，置于列表y中
    y = []
    y[0] = card.pos[1]
    y[1] = 2 * height + card.pos[1]
    y[2] = 2 * height - card.pos[1]
    y[3] = -card.pos[1]
    y[4] = -2 * height + card.pos[1]
    # 到达道具位置用时
    card_step = abs(x0 - card.pos[0]) // vx0
    # 在能到达道具的一系列速度中挑选出属于区间v_range的，保存到列表中并返回
    # 列表中的元素类型是int
    return [vy for vy in
        filter(lambda v: (v >= v3 and v <= v2)or(v >= v1 and v <= v0),
               map(lambda x: (x - y0) // card_step, y))]

def ball_fly_to_card(b_d:tuple, cards_al:list) -> list:
    """
    cards_al means cards_available
    根据桌面上现有的道具种类、位置和球所在的位置，计算吃到对应的各个道具所需要的竖直速度
    :param b_d: b_d = (tb.ball['position'].x,tb.ball['position'].y,tb.ball['velocity'].x,tb.ball['velocity'].y,tb.tick)
    :param cards_al: list，决策前桌面上道具的信息，元素是Card类
    :param height: 球桌宽度，DIM[3] - DIM[2]
    :param v_range: 满足规则（碰撞1-2次）的速度区间[v3,v2]∪[v1,v0]
    :return: 返回一个list，其元素为符合击中某道具要求的竖直速度群，vy_list的元素和cards_al的元素是对应关系
    """
    v_range = ball_v_range(b_d)
    # 吃到序号为i的道具需要的速度（所有可能的速度）保存在v[i]中
    vy_list = []
    for i in range(len(cards_al)):
        vy_list[i] = fly_assistant(b_d, v_range, cards_al[i])
    # 返回吃到所有道具所需要的竖直速度，通过对应索引查找
    return vy_list


