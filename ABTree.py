class node:
    '''
    节点类，每个节点对应一个棋盘状态。
    '''
    def __init__(self, tb, level, isMe):
        '''
        初始化节点
        :param tb: 节点信息
        :param level: 当前距离估值需要的层数。为0时，调用估值函数
        '''
        self.tb = tb
        self.level = level
        # 判断是否是己方节点。决定了max和min
        self.isMe = isMe
        # 指示遍历完成后，选择第几个决策
        self.action = None
        # 指向子节点的node
        self.decision = []
        # 决策值，本步采取最佳决策时的估值。用于上层节点估值
        self.value = None

    def evaluate(self):
        '''
        估值函数，目前是空实现
        注意最后一步需要根据是自己还是对方节点返回正、负值
        :return: 叶子节点估值
        '''
        # TODO 估值具体实现
        pass
    def fillChild(self, getAction = False):
        '''
        为self.decision填充内容，即添加子节点。子节点和本节点类型不同
        :param getAction: 只有根节点需要，获得每个子节点达到的操作方式
        :return: None或RacketData
        '''
        # TODO 添加子节点具体实现
        pass

class NegaMaxTree:
    '''
    NegaMax博弈树
    '''
    def __init__(self, root:node):
        self.root = root
    def traverse(self, data = None, level:int = 6):
        '''
        遍历博弈树，用NegaMax方法搜得最佳子节点
        :return: 返回操作和估值
        '''
        if data is None:
            data = {}
        # 初始化根节点
        node = self.root
        ini_level = level
        action = node.fillChild(True)
        stack = [(node, 0, level)]
        # 遍历，栈空时结束
        while stack:
            # 弹出一级的节点，index指已经完成遍历的子节点个数
            node, index, level = stack.pop()
            # 如果为叶子，则返回估值
            if level == 0:
                node.value = node.evaluate()
            # 如果为枝干末尾，则汇总出子节点最大值，作为本节点的最终估值
            elif index == len(node.decision):
                # 如果是ini_level，需要返回所在位置（而其实不需要博弈值），否则只需要一个博弈值
                # enumertate把一个迭代器的元素变成一个元组，第一项是序号。
                max_group= max(*enumerate(node.decision), key = lambda x:x[1].value)
                node.value = max_group[1].value
                if level == ini_level:
                    node.action = max_group[0]

            # 如果是一个普通的支，则进行下一轮遍历
            else:
                newNode = node.decision[index]
                # 入栈，把本节点和下一轮节点入栈
                stack.append((node, index + 1, level))
                stack.append((newNode, 0, level-1))
                # 第一次遍历，如果子节点不是叶子，需要动态生成子节点列表
                newNode.fillChild()

    def __str__(self):
        '''
        返回一个可读的、树的字符串表达
        这一步需要在构建博弈树完成之后。用广度优先搜索。
        :return: 
        '''
        queue = [self.root]
        node = self.root
        s = ''
        # 队列不空
        while queue:
            node = queue.pop(0)
            if node is None:
                s += '|'
            else:
                s += str(node.value) + ','
                queue.extend(node.decision)
                # 为了分隔各层，添加标识
                queue.append(None)
        return s