import unittest
class myclass:
    def sum( x, y):
        return x+y
    def sub( x, y):
        return x-y

class mytest(unittest.TestCase):
    #初始化工作
    def setUp(self):
        pass
    #退出清理工作
    def tearDown(self):
        pass
    #具体的测试用例，一定要以test开头
    def testsum(self):
        self.assertEqual(myclass.sum(1, 2), 3, 'test sum fail')
    def testsub(self):
        self.assertEqual(myclass.sub(2, 1), 1, 'test sub fail')

if __name__ =='__main__':
  unittest.main()