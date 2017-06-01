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

def play(tb: TableData, ds) -> RacketAction:
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
    b_d = (tb.ball['position'].x, tb.ball['position'].y, tb.ball['velocity'].x, tb.ball['velocity'].y, tb.tick)
    # 创建player_data（迎球方）和op_player_data（跑位方）元组
    p_d = (tb.side["life"], tb.side['position'].y, tb.side['cards'])
    op_d = (tb.op_side["life"], tb.op_side["active_card"], tb.op_side['position'].y)
    # 创建cards元组
    cards = (tb.cards['card_tick'], tb.cards['cards'])
    # TODO 创建道具Series
    # ——————————————————————————————————————————————————————————————————————————————#
    y0, v0 = b_d[1], b_d[3]
    # cards_available:桌面上现有的道具列表，元素为Card类
    cards_available = cards[1]
    # 对方上一轮迎球加速跑位加减血道具生效而我方尚未作出迎球反应时双方体力值
    p_life1, op_life1 = p_d[0], op_d[0]
    # 我方拥有的道具list,为CardBox类
    p_cards = p_d[2]

    # TODO 改系数，获得合理的等距v的Series，会用到ball_v_range(b_d)
    p_v = pd.Series([1000 * i for i in range(50)])

    # v_will_hit:list，其元素为list，即为符合击中某道具要求的竖直速度群，vy_list的元素和cards_al的元素是对应关系
    v_will_hit = ball_fly_to_card(b_d, cards_available)
    for card_i in v_will_hit:
        p_v.append(pd.Series(card_i))

    # y1：Series为到达对方时球的y轴坐标，v1：Series，为到达对方时球的y轴速度
    # op_chosen_v为对方回球的y轴速度，为Series
    y1, v1 = ball_fly_to(y0, p_v)
    op_chosen_v = op_play(y0, y1, v1)

    # 计算双方决策后的“体力值”
    # 对于我方而言，不等同于体力值，因为加入了获得道具的“加分”。而且为了避免“吃老本”的情况，没有考虑加减血包的使用。
    # 对对方而言，也不等同于体力值，因为是只考虑一小部分的体力估值
    p_life2, p_active_SPIN, p_active_AMPL = p_life_consume(b_d, p_d, op_d, cards_available, p_v, op_chosen_v, y1)
    op_life2 = op_life_consume(op_d, y0, op_chosen_v, y1, p_active_SPIN, p_active_AMPL)
###########TODO ！！！！！！！！！！！！！！！！！！！！！！！！！！！！！！！！！！
    # 获得我方估值函数值中的最大值对应索引
    p_path_assume = (p_life2 - p_life1) - (op_life2 - op_life1)
    index = p_path_assume.argmax()

    # 返回具体打球方式
    p_chosen_v = p_v[index]
    p_chosen_side = p_card_side[index]
    p_chosen_card = p_active_card[index]
    # 如果没有使用道具而恰好有加减血包，现在是优先使用减血包，属于攻击性策略。
    if p_chosen_side == None and p_chosen_card == None:
        if CARD_DECL in p_cards:
            p_chosen_side = 'OPNT'
            p_chosen_card = CARD_DECL
        elif CARD_INCL in p_cards:
            p_chosen_side = 'SELF'
            p_chosen_card = CARD_INCL
        else:  # 扔掉隐身术
            if CARD_DSPR in p_cards:
                p_chosen_side = 'SELF'
                p_chosen_card = CARD_DSPR
    # TODO 还要加入对方使用旋转球的应对
    return RacketAction(tb.tick, tb.ball['position'].y - tb.side['position'].y, p_chosen_v - v0, 0, p_chosen_side,p_chosen_card)


def p_life_consume(b_d:tuple, p_d:tuple, op_d:tuple, cards_available: list, p_v: pd.Series, op_chosen_v: pd.Series, y1: pd.Series):
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
    # 我方拥有的道具list,为CardBox类
    p_cards = p_d[2]
    p_life = p_d[0]
    # op_ini_pos 对手跑位前位置
    op_active_card, op_ini_pos = op_d[1], op_d[2]
    y0, v0 = b_d[1], b_d[3]

    # 以下对道具获取路径额外加分，对击中不同的道具的p_v路径给予不同的p_life“加分”，以便估值函数能显示出走这条能获得道具的路更有益
    # 由于最后计算p和op的life差值，op的减分统一加在p_life上，PS：card_i是Card类。
    # TODO 除加减血包外道具加分有待调整
    for card_i in cards_available:
        if p_v in card_i:
            if card_i == CARD_INCL or card_i == CARD_DECL:
                # CARD_INCL_PARAM和CARD_DECL_PARAM都为2000
                p_life += 2000
            elif card_i == CARD_TLPT:
                p_life += 918
            elif card_i == CARD_AMPL:
                p_life += 918
            elif card_i == CARD_SPIN:
                p_life += 918
    '''
    以下是具体决策结果实现部分
    只考虑变压器、旋转球、瞬移术的使用，优先使用旋转球变压器，属于进攻性策略。
    这里和路径选取以及道具获取没有关系，考虑旋转、变压、瞬移道具（如果有）的使用，受益是否超过设定值，超过则用。
    以上使用内部还应该根据实际情况划出优先级。
    '''
    # y2和v2是对方决策后在我方的落点以及我方的速度，都为Series
    y2, v2 = ball_fly_to(y1, op_chosen_v)
    # 我方决策跑位到 对方决策后在我方的落点 与 当下位置的中点
    middle = (y2 + p_d[1]) // 2

    # TODO 道具的具体使用的阈值调整以及策略变动
    # 估值函数里不考虑加血包减血包的使用

    # p_active_XXXX 为Series，元素类型为bool
    # 旋转球的使用（如果秒杀则使用）
    if CARD_SPIN in p_cards:
        p_active_SPIN = sec_kill(p_v, y0)
    else:
        p_active_SPIN = None
    # 变压器的使用（对方总移动超过一半）
    if CARD_AMPL in p_cards:
        p_active_AMPL = (y1 - op_ini_pos).apply(abs) > Height * 0.5
    else:
        p_active_AMPL = None
    # 瞬移术的使用（跑位超过一半）
    if CARD_TLPT in p_cards:
        p_active_TLPT = (middle - y0).apply(abs) > Height * 0.5
    else:
        p_active_TLPT = None

    # 获取我方可能的决策结果 RacketAction(b_d[4], y0 - p_d[1], p_v - v0, middle, p_card_side, p_active_card)
    # 将迎球方动作中的距离速度等值规整化为整数
    player_action_bat = (y0 - p_d[1]).apply(int) # t0~t1迎球的动作矢量（移动方向及距离）
    player_action_acc = (p_v - v0).apply(int)  # t1触球加速矢量（加速的方向及速度）
    player_action_run = middle.apply(int)# t1~t2跑位的动作矢量（移动方向及距离）
    # player_action_card = (p_card_side, p_active_card)  # 对'SELF'/'OPNT'使用道具

    # 球拍的全速是球X方向速度，按照体力值比例下降
    velocity = int((p_life / RACKET_LIFE) * BALL_V[1])
    # bat_distance 为指定迎球的距离
    bat_distance = player_action_bat

    # 如果指定迎球的距离大于最大速度的距离，则丢球，比赛结束
    if abs(bat_distance) > velocity * STEP:
        return False

    # 按照迎球的距离减少体力值（考虑对方之前可能使用变压器道具）
    p_life -= (abs(bat_distance) ** 2 // FACTOR_DISTANCE ** 2) * (CARD_AMPL_PARAM if op_active_card == CARD_AMPL else 1)
    # 按照给球加速度的指标减少体力值（考虑对方之前可能使用变压器道具）
    p_life -= (abs(player_action_acc) ** 2 // FACTOR_SPEED ** 2) * (CARD_AMPL_PARAM if op_active_card == CARD_AMPL else 1)

    # 如果指定跑位的距离大于最大速度的距离，则采用最大速度距离
    run_distance = player_action_run.apply(sign) * \
                   player_action_run.apply(abs).where(player_action_run.apply(abs) < velocity * STEP,velocity * STEP)
    # \后面的代码作用于int时为 min(abs(player_action_run), velocity * STEP)

    # 按照跑位的距离减少体力值（考虑我方可能使用瞬移卡道具）
    param = 0
    if CARD_TLPT in p_cards: # 如果使用瞬移卡，从距离减去CARD_TLPT_PARAM再计算体力值减少
        param = CARD_TLPT_PARAM

    a = (run_distance.apply(abs) - param) ** 2 // FACTOR_DISTANCE ** 2
    b = run_distance.apply(sign) - param
    p_life -= a.where(b > 0, 0)
    '''# 作用于int时的代码 
    if sign(run_distance) - param > 0:
        p_life -= (abs(run_distance) - param) ** 2 // FACTOR_DISTANCE ** 2'''

    # 返回执行决策后p_life,p_card_side和p_active_card
    return p_life, p_active_SPIN, p_active_AMPL


def op_life_consume(op_d, y0, op_chosen_v, y1, p_active_SPIN, p_active_AMPL)->pd.Series:
    """
    根据我方此次决策，算出迎球+加速+跑位的总体力消耗(考虑道具)
    :param p_active_SPIN: Series，不同路径使用CARD_SPIN的情况，元素为bool
    :param p_active_AMPL: Series，不同路径使用CARD_AMPL的情况，元素为bool
    :param p_active_TLPT: Series，不同路径使用CARD_TLPT的情况，元素为bool
    :param op_d = (tb.op_side["life"], tb.op_side["active_card"])
    :return: 执行完决策后对方体力值
    """
    op_life = op_d[0]
    op_vy = op_chosen_v
    op_y = y1

    # 对方决策在我方处的落点
    y2, v2 = ball_fly_to(op_y, op_vy)
    # 对方跑位到我方落点与当下位置中某一点
    middle = Ct * (y2 - op_y) + op_y

    # 获取对方的决策结果
    # TODO 还要当我方使用旋转球时加入对方的应对

    # 获取对方可能的决策结果 RacketAction(7200, Ct * (y2 - y0) + y0, op_vy - v2, middle, None, None) 下文中tick没用，随便取一个合法值
    # 将迎球方动作中的距离速度等值规整化为整数
    op_player_action_bat = (Ct * (y2 - y0) + y0).apply(int)  # t0~t1迎球的动作矢量（移动方向及距离）
    op_player_action_acc = (op_vy - v2).apply(int)  # t1触球加速矢量（加速的方向及速度）
    op_player_action_run = middle.apply(int)  # t1~t2跑位的动作矢量（移动方向及距离）


    # 球拍的全速是球X方向速度，按照体力值比例下降
    velocity = int((op_life / RACKET_LIFE) * BALL_V[1])

    # 如果指定迎球的距离大于最大速度的距离，则丢球，比赛结束
    # TODO 这个False可能有问题
    if abs(op_player_action_bat) > velocity * STEP:
        return False

    # 按照迎球的距离以及给球加速度的指标减少体力值（考虑我方可能使用变压器道具）
    a = op_player_action_bat.apply(abs) ** 2 // FACTOR_DISTANCE ** 2 + op_player_action_acc.apply(abs) ** 2 // FACTOR_SPEED ** 2
    b = pd.Series(CARD_AMPL_PARAM, range(op_chosen_v.size))
    op_life -= a * b.where(p_active_AMPL, 1)
    '''# 作用于int时的代码
    # 按照迎球的距离减少体力值（考虑我方可能使用变压器道具）
    op_life -= (abs(op_player_action_bat) ** 2 // FACTOR_DISTANCE ** 2) * (CARD_AMPL_PARAM if p_active_card == CARD_AMPL else 1)
    # 按照给球加速度的指标减少体力值（考虑我方可能使用变压器道具）
    op_life -= (abs(op_player_action_acc) ** 2 // FACTOR_SPEED ** 2) * (CARD_AMPL_PARAM if p_active_card == CARD_AMPL else 1)
    '''
    # 如果指定跑位的距离大于最大速度的距离，则采用最大速度距离
    run_distance = op_player_action_run.apply(sign) * \
                   op_player_action_run.apply(abs).where(op_player_action_run.apply(abs) < velocity * STEP,velocity * STEP)
    # \后面的代码作用于int时为 min(abs(op_player_action_run), velocity * STEP)

    # 按照跑位的距离减少体力值（听说对方不用道具）
    op_life -= run_distance.apply(abs) ** 2 // FACTOR_DISTANCE ** 2
    # 返回执行决策后op_life
    return op_life


def op_play(y0:int, y1: pd.Series, v1: pd.Series):
    """
    面对(y1,v1)，对手的选择
    :param y1: pd.Series，打到对手底线时球的y轴坐标
    :param v1: pd.Series，打到对手底线时球的y轴速度
    :param op_v: Series，对手可能的回球方式
    :param op_assume: Series，对手可能的回球方式的估值函数值
    :return: int，对手最终决定的回球方式
    """
    # TODO 改系数，获得合理的等距v的Series
    op_v = pd.Series([1000 * i for i in range(5)])
    op_assume = (op_v.apply(op_assume_f, y1=y1, v1=v1, y0=y0)).apply(lambda x : x[x.idxmax()],axis = 1)
    op_chosen_v = op_v[op_assume.argmax()]
    return op_chosen_v


def op_assume_f(op_v:int, y1: pd.Series, v1: pd.Series, y0:int) ->pd.Series:
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
    op_lose = (((op_v - v1) / FACTOR_SPEED) ** 2).apply(int)
    # 我方将从y0跑位至y0和y2之间的某一点，并到y2处迎球
    y2 = mirror2real(y1 + 1800 * op_v)[0]
    # C为可调试的常数，取值范围0.5-1，
    p_lose = (C * ((y0 - y2) / FACTOR_DISTANCE) ** 2).apply(int)
    return p_lose - op_lose


def ball_fly_to(y: int, v: int) -> tuple:
    """
    根据出射点坐标、出射速度，算出到达对侧位置速度
    注意，虽然函数参数为int，但是因为计算过程只涉及四则，y,v皆可为Series并直接调用
    :param y0: 出射点坐标
    :param p_v: int，出射速度
    :param Y: int，镜像点y坐标
    :param count: 与桌碰撞次数，可正可负
    :return: 到达对侧位置位置、速度
    """
    # Y 为没有墙壁时乒乓球到达的位置（镜像点）
    Y = y + v * STEP
    # 把镜像点转化为真实点
    yi = mirror2real(Y)[0]
    # 计算并更新y轴速度
    count = mirror2real(Y)[1]
    vi = v * ((count + 1) % 2 * 2 - 1) # 后面这一项，当count为偶数时为1，奇数时为-1
    return yi, vi


def mirror2real(y_mr: int or np.array or pd.Series) -> tuple:
    """
    将镜像点映射为真实点.
    可以代入int,np.array,pd.Series等多种类型
    :param y_mr: 镜像点y坐标
    :return: 真实点y坐标数组（范围0-1,000,000），碰撞次数数组
    """
    if type(y_mr) is int:
        if y_mr % (2 * Height) < Height:
            y_real = y_mr % Height
        else:
            y_real = Height - y_mr % Height
        # 若球没有打在边界上
        if y_mr % Height != 0:
            count = y_mr // Height
        else:
            count = (y_mr // Height if (y_mr > 0) else (1 - y_mr // Height))
        return y_real, count
    elif type(y_mr) is np.array:
        # 以上代码用np.array改写形式
        y_real = np.where(y_mr % (2 * Height) < Height, y_mr % Height, Height - y_mr % Height)
        count = np.where(y_mr % Height != 0, y_mr // Height,
                         np.where(y_mr > 0, y_mr // Height, 1 - y_mr // Height))
        return y_real, count
    elif type(y_mr) is pd.Series:
        # 以上代码用pd.Series改写形式
        y_mr = y_mr.values
        # 复制ndarray
        y_real = np.where(y_mr % (2 * Height) < Height, y_mr % Height, Height - y_mr % Height)
        count = np.where(y_mr % Height != 0, y_mr // Height,
                         np.where(y_mr > 0, y_mr // Height, 1 - y_mr // Height))
        return pd.Series(y_real), pd.Series(count)


def ball_fly_to_card(b_d: tuple, cards_al: list) -> list:
    """
    cards_al means cards_available
    根据桌面上现有的道具种类、位置和球所在的位置，计算吃到对应的各个道具所需要的竖直速度
    :param b_d: b_d = (tb.ball['position'].x,tb.ball['position'].y,tb.ball['velocity'].x,tb.ball['velocity'].y,tb.tick)
    :param cards_al: list，决策前桌面上道具的信息，元素是Card类
    :param height: 球桌宽度，DIM[3] - DIM[2]
    :param v_range: 满足规则（碰撞1-2次）的速度区间[v3,v2]∪[v1,v0]
    :return: 返回一个list，其元素为list，即为符合击中某道具要求的竖直速度群，vy_list的元素和cards_al的元素是对应关系
    >>> ball_fly_to_card((-900000, 80000, 1000, 50), [Card('SP', 0.5, Vector(200,10000))])
    [[-78, -100]]
    """
    v_range = ball_v_range(b_d)
    # 吃到序号为i的道具需要的速度（所有可能的速度）保存在v[i]中
    vy_list = [0] * len(cards_al)
    for i in range(len(cards_al)):
        vy_list[i] = fly_assistant(b_d, v_range, cards_al[i])
    # 返回吃到所有道具所需要的竖直速度，通过对应索引查找
    return vy_list


def fly_assistant(b_d: tuple, v_range: tuple, card: Card) -> list:
    """
    根据某个确定的道具位置和球所在的位置，计算吃到它所需要的竖直速度
    :param b_d: b_d = (tb.ball['position'].x,tb.ball['position'].y,tb.ball['velocity'].x,tb.ball['velocity'].y,tb.tick)
    :param v_range: 满足规则（碰撞1-2次）的速度区间[v3,v2]∪[v1,v0]
    :param card: 是一个Card类
    :param x0: x0 = b_d[0]，接球时球的横坐标
    :param y0: y0 = b_d[1]，接球时球的纵坐标
    :param vx0: vx0 = b_d[2]，球的水平速度
    :return: 返回一个list，元素为符合击中某道具要求的竖直速度
    >>> print(fly_assistant((-900000, 80000, 1000, 50), ball_v_range((-900000, 80000, 1000, 50)), Card('SP', 0.5, Vector(200,10000))))
    [-78, -100]
    """
    x0, y0, vx0 = b_d[0], b_d[1], b_d[2]
    # 满足规则（碰撞1-2次）的速度区间[v3,v2]∪[v1,v0]
    v0, v1, v2, v3 = v_range
    # 要吃的道具共有五个可能的镜像点/真实点，置于列表y中
    y = [0] * 5
    y[0] = card.pos.y
    y[1] = 2 * Height + card.pos.y
    y[2] = 2 * Height - card.pos.y
    y[3] = -card.pos.y
    y[4] = -2 * Height + card.pos.y
    # 到达道具位置用时
    card_step = abs(x0 - card.pos.x) // vx0
    # 在能到达道具的一系列速度中挑选出属于区间v_range的，保存到列表中并返回
    # 列表中的元素类型是int
    return [vy for vy in
            filter(lambda v: (v >= v3 and v <= v2) or (v >= v1 and v <= v0),
                   map(lambda x: (x - y0) // card_step, y))]


def ball_v_range(b_d: tuple) -> tuple:
    """
    根据我方出射点坐标，算出y轴可取速度的边界值
    :param STEP: 1800 tick
    :param b_d[2]: b_d[2] = tb.ball['position'].y,接球时球的纵坐标
    :return: 可取速度的边界
    """
    # v0,v1,v2,v3是速度的范围边界:可取[v3,v2]∪[v1,v0]
    v0 = (3 * Height - b_d[2]) // STEP
    v1 = (1 * Height - b_d[2]) // STEP + 1
    v2 = (0 - b_d[2]) // STEP
    v3 = (-2 * Height - b_d[2]) // STEP + 1
    # 贴边打的情况算作反弹零次，需要排除
    if v2 == 0:
        v2 = -1
    elif v1 == 0:
        v1 = 1
    # 返回一个元组，依次为速度的四个边界值
    return v0, v1, v2, v3


def sec_kill(p_v: pd.Series, y0: int) -> pd.Series:
    """
    根据我方出射点坐标速度，判断对方简单反弹时是否可以秒杀
    :param p_v:pd.Series，出射点坐标速度
    :param y0:int，出射点坐标坐标
    :return: pd.Series  元素为bool类型
    >>> a = sec_kill(pd.Series(range(-1000, 400)), 10)
    >>> print(a[a].count(), a.count())
    842 1400
    """
    # 镜像点坐标。Y:pd.Series
    Y = y0 + STEP * p_v
    # 把镜像点Y转化为真实点，然后求合法速度区间
    y, count = mirror2real(Y)
    v_range = ball_v_range(y)
    # 对方接球时的竖直速度函数
    # 这句写给金老师：pd.Series直接不能用where，但是pd.Series.values返回值的np.array，可以用np.where。彻底解决。
    # 另外pd.Series基于np.array实现，两种类型几乎是秒转换，不必担心效率。

    # op_v = p_v if (count % 2 == 0) else (- p_v)
    op_v = pd.Series(np.where(count.values % 2 == 0, p_v, -p_v))
    # 返回True or False，True表示会被秒杀，False表示不会
    # 经测试，逻辑连接符可以用&|-表示与或非，但是似乎不可以用and,or,not。注意优先级不同，必须加括号
    return -(((op_v >= v_range[3]) & (op_v <= v_range[2])) | ((op_v >= v_range[1]) & (op_v <= v_range[0])))
