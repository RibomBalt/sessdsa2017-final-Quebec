def ball_flyto(tb, ticks):  # 球运动，更新位置，并返回触壁次数和路径经过的道具（元组）
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

def ball_v_range(tb,ticks):
    # v0,v1,v2,v3是速度的范围边界
    v0 = (3 * tb.ball.extent[3] - tb.ball.pos.y) / ticks
    v1 = (1 * tb.ball.extent[3] - tb.ball.pos.y) / ticks
    v2 = (0 - tb.ball.pos.y) / ticks
    v3 = (-2 * tb.ball.extent[3] - tb.ball.pos.y) / ticks
    return v0, v1, v2, v3

