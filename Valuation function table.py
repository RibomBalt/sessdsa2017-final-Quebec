import csv
from T_Bamboo import op_player_f
from T_Bamboo import player_f

def ball_v_range(y):
    """
    根据我方出射点坐标，算出y轴可取速度的边界值
    :param tb.step: 1800 tick
    :param Y: 镜像点y坐标
    :param height: 乒乓球桌的宽度, DIM[3] - DIM[2]
    :return: 与桌碰撞次数
    """
    STEP = 1800
    height = 1800000
    # v0,v1,v2,v3是速度的范围边界:[v3，v2]∪[v1，v0]
    v0 = (3 * height - y) // STEP
    v1 = (1 * height - y) // STEP + 1
    v2 = (0 - y) // STEP
    v3 = (-2 * height - y) // STEP + 1
    if v2 == 0:
        v2 = -1
    return (v0, v1, v2, v3)


csvfile = open('max.csv', 'w')


writer = csv.writer(csvfile, lineterminator='\n')
writer.writerow([('初速度v0', '位置y0', '最大值v')])
for y0 in range(0, 1001):
    y0 = y0 * 100
    print('y0 =',y0,'-------',ball_v_range(y0))
    v_range = ball_v_range(y0)
    v0 = v_range[0]
    v1 = v_range[1]
    v2 = v_range[2]
    v3 = v_range[3]
    for vo in range(-100, 100):
        vo = vo * 10
        op_cost = 0
        for v in range(v3, v2):
            temp = op_player_f(v, vo, y0)
            if op_cost < temp:
                v_me = v
                op_cost = temp
        for v in range(v1, v0):
            if op_cost < temp:
                v_me = v
                op_cost = temp

        data = [(vo, y0,v_me)]
        print(vo, y0,v_me,v_range)
        writer.writerows(data)

csvfile.close()

csvfile = open('max.csv', 'r')
reader = csv.reader(csvfile)
for row in reader:
    print(row)

csvfile.close()
if __name__ == '__main__':
    # csv.main()
    pass
