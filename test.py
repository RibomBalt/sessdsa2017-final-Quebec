# 从table中导入所有常量
from table import *

# # 桌面的坐标系，单位"pace"
# DIM = (-900000, 900000, 0, 1000000)
# # 最大时间，单位"tick"，每个回合3600tick，200回合
# TMAX = 800000
# # 球的初始坐标(x,y)，在west中间
# BALL_POS = (DIM[0], (DIM[3] - DIM[2]) // 2)
# # 球的初速度，(vx,vy)，单位"p/t"，向东北飞行
# BALL_V = (1000, 1000)
# # 球拍的生命值，100个回合以上
# RACKET_LIFE = 100000
# # 迎球和跑位扣减距离除以系数的平方（LIFE=0-10000)
# FACTOR_DISTANCE = 10000
# # 加速则扣减速度除以系数结果的平方（LIFE=0-400)
# FACTOR_SPEED = 50
# # 游戏方代码
# PL = {'West': 'W', 'East': 'E'}
# # 游戏结束原因代码
# RS = {'invalid_bounce': 'B', 'miss_ball': 'M', 'life_out': 'L', 'time_out': 'T'}
# # 道具出现频率每多少ticks出现一个道具
# CARD_FREQ = 40000
# # 道具出现的空间范围
# CARD_EXTENT = (-800000, 800000, 100000, 900000)
# # 道具箱的最大容量
# MAX_CARDS = 3
# # 球桌上最多道具
# MAX_TABLE_CARDS = 10
# # 卡牌代码
# CARD_SPIN = 'SP'  # 旋转球：用于抵消被用道具方施加在球拍上的加速，使之正常反弹回来；param=0，增加的速度乘以parm
# CARD_SPIN_PARAM = 0
# CARD_DSPR = 'DS'  # 隐身术：隐藏被用道具方的位置和跑位方向1次；param=0，位置乘以parm，方向乘以parm
# CARD_DSPR_PARAM = 0
# CARD_INCL = 'IL'  # 补血包：给被用道具方补血（增加体力值）；param=2000，life加上param
# CARD_INCL_PARAM = 2000
# CARD_DECL = 'DL'  # 掉血包：给被用道具方减血（减少体力值）；param=2000，life减去param
# CARD_DECL_PARAM = 2000
# CARD_TLPT = 'TP'  # 瞬移术：被用道具方可以移动一段距离而不消耗体力值；param=250000，只作用在迎球阶段
# CARD_TLPT_PARAM = 250000
# CARD_AMPL = 'AM'  # 变压器：放大被用道具方的体力值损失；param=2；体力值损失增加1倍。
# CARD_AMPL_PARAM = 2
# ALL_CARDS = [(CARD_SPIN, CARD_SPIN_PARAM), (CARD_DSPR, CARD_DSPR_PARAM), (CARD_INCL, CARD_INCL_PARAM),
#              (CARD_DECL, CARD_DECL_PARAM), (CARD_TLPT, CARD_TLPT_PARAM), (CARD_AMPL, CARD_AMPL_PARAM)]


# 球运动，更新位置，并返回触壁次数
def ball_fly_to(tb, ticks):
    # x方向的位置
    tb.ball.pos.x += tb.ball.velocity.x * ticks
    # Y 没有墙壁时到达的位置
    Y = tb.ball.velocity.y * ticks + tb.ball.pos.y
    if Y % tb.ball.extent[3] != 0:  # 未在边界
        count = Y // tb.ball.extent[3]
        tb.ball.pos.y = (Y - count * tb.ball.extent[3]) * (1 - 2 * (count % 2)) + tb.ball.extent[3] * (count % 2)
        tb.ball.velocity.y = tb.ball.velocity.y * ((count + 1) % 2 * 2 - 1)
        return abs(count)
    else:  # 恰好在边界
        count = (Y // tb.ball.extent[3]) if (Y > 0) else (1 - Y // tb.ball.extent[3])
        tb.ball.pos.y = Y % (2 * tb.ball.extent[3])
        tb.ball.velocity.y = tb.ball.velocity.y * ((count + 1) % 2 * 2 - 1)
        return abs(count)

def ball_v_range(tb, ticks):
    # v0,v1,v2,v3是速度的范围边界
    v0 = (3 * tb.ball.extent[3] - tb.ball.pos.y) / ticks
    v1 = (1 * tb.ball.extent[3] - tb.ball.pos.y) / ticks
    v2 = (0 - tb.ball.pos.y) / ticks
    v3 = (-2 * tb.ball.extent[3] - tb.ball.pos.y) / ticks
    return v0, v1, v2, v3


def life_consume(tb):
    # 首先取得迎球方和跑位方的对象
    player = tb.players[tb.side]
    op_player = tb.players[tb.op_side]
    # 跑位方的道具生效
    tb.active_card = op_player.action.card
    # 迎球方掉血
    if tb.active_card[1] == CARD_DECL:
        player.life -= CARD_DECL_PARAM
    # 跑位方加血
    if tb.active_card[1] == CARD_INCL:
        op_player.life += CARD_INCL_PARAM
    dict_side = {'position': copy.copy(player.pos),
                 'life': player.life,
                 'cards': copy.copy(player.card_box)}
    dict_op_side = {'position': None if tb.active_card[1] == CARD_DSPR else copy.copy(op_player.pos),
                    'life': op_player.life,
                    'cards': copy.copy(op_player.card_box),
                    'active_card': tb.active_card,
                    'accelerate': None if tb.active_card[1] == CARD_DSPR else
                    (-1 if op_player.action.acc < 0 else 1),
                    'run_vector': None if tb.active_card[1] == CARD_DSPR else
                    (-1 if op_player.action.run < 0 else 1)}
    dict_ball = {'position': copy.copy(tb.ball.pos),
                 'velocity': copy.copy(tb.ball.velocity)}
    dict_card = {'card_tick': tb.card_tick,
                 'cards': copy.copy(tb.cards)}
    # 调用，返回迎球方的动作
    player_action = player.play(TableData(tb.tick, tb.tick_step,dict_side, dict_op_side, dict_ball, dict_card),player.datastore)
    # 设置迎球方的动作，将迎球方动作中的距离速度等值规整化为整数
    player_action.normalize()
    player.set_action(player_action)

    # 执行迎球方的两个动作：迎球和加速
    player.update_pos_bat(tb.tick_step, tb.active_card)
    player.update_acc(tb.active_card)
    tb.ball.update_velocity(player.action.acc, tb.active_card)
    return player.life

def op_acc(tb, ticks):
    # Y 没有墙壁时到达的位置
    Y = -tb.ball.velocity * ticks + tb.ball.pos.y
    count = Y // tb.ball.extent[3]
    return tb.ball.velocity * ((count + 1) % 2 * 2 - 1)-111 # 我没看明白之前的数据怎么调用？？？这里应该减之前的vy？？

# 这里是杨帆的处理方式，因为所有点都是整数，那么假设墙壁不存在
def yspeed2mirror(y_speed:int, o_axis:int):
    """
    将镜像点映射为真实点
    :param y_speed: y向速度
    :param o_axis: 发球点的y坐标，原点、镜点均可
    :return: 返回打到的镜点
    """
    # 目前没有更加方便借鉴的常数
    return o_axis + y_speed * 3600

def mirror2real(y_axis:int):
    """
    将镜像点映射为真实点
    :param o_axis: 原点的真实y坐标（一般代发球点的真实y坐标）
    :param y_axis: 镜像点y坐标
    :return: 真实点y坐标，范围0-1,000,000
    """
    n_mirror, remain = divmod(y_axis, DIM[3])
    # n_mirror是穿过墙的数目
    return {0:remain, 1:DIM[3] - remain}[n_mirror % 2]