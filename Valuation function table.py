import csv
import numpy as np
import matplotlib.pyplot as plt
from table import *
from T_Bamboo import op_player_f
from T_Bamboo import player_f

def ball_v_range(y:int) -> tuple:
    """
    根据我方出射点坐标，算出y轴可取速度的边界值
    :param STEP: 1800 tick
    :param height: 乒乓球桌的宽度, DIM[3] - DIM[2]
    :param y: 接球时球的纵坐标
    :return: 可取速度的边界
    """
    STEP = 1800
    height = DIM[3] - DIM[2]
    # v0,v1,v2,v3是速度的范围边界:可取[v3,v2]∪[v1,v0]
    v0 = (3 * height - y) // STEP
    v1 = (1 * height - y) // STEP + 1
    v2 = (0 - y) // STEP
    v3 = (-2 * height - y) // STEP + 1
    # 贴边打的情况算作反弹零次，需要排除
    if v2 == 0:
        v2 = -1
    # 返回一个元组，依次为速度的四个边界值
    return v0, v1, v2, v3

def traversal():
    csvfile = open('op_player_f.csv', 'wb')
    writer = csv.writer(csvfile, lineterminator='\n')
    writer.writerow([('给定初速度vi', '给定纵坐标yi', '最值对应速度v')])
    for yi in range(0, 1000001, 100000):
        v_range = ball_v_range(yi)
        v0, v1, v2 ,v3 = v_range
        print('yi =', yi, '-------', v_range)
        for vi in range(-1000,1000,20):
            '''
            op_cost = 0
            for v in range(v3, v2 + 1):
                temp = op_player_f(v, vi, yi)
                if op_cost < temp:
                    v_me = v
                    op_cost = temp
            for v in range(v1, v0 + 1):
                temp = op_player_f(v, vi, yi)
                if op_cost < temp:
                    v_me = v
                    op_cost = temp

            '''
            data = [(vo, y0,v_me)]
            print(vo, y0,v_me,v_range)
            writer.writerows(data)
    csvfile.close()
    '''
    # 在pycharm上面输出结果
    csvfile = open('max.csv', 'r')
    reader = csv.reader(csvfile)
    for row in reader:
        print(row)
    csvfile.close()
    '''

def f(v):
    y = op_player_f(v, 500, 900000)
    return y

# 定义自变量如何取值
xx = np.arange(-1000, 2000, 20)
def calc():  # 计算并绘图
    a, b = [], []  # 建立绘制点的坐标列表
    for x in xx.tolist():  # 要将array对象转换成列表对象
        # det = np.matrix(x)
        a.append(x)
        b.append(f(x))
    plt.plot(a, b)  # 绘制图形
    plt.show()  # 显示图形
if __name__ == '__main__':
    print(ball_v_range(900000))
    calc()