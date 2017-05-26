# 常见问题

Q：**自己写的算法serve发球函数可以返回任意位置和速度吗？
是否消耗体力？**

A：可以返回发球的任意位置和速度，但要符合反弹1-2次的强制要求，
由于没有移动球拍，所以不消耗体力值。但发球方不能实施跑位，所以算是抵消先手优势。

Q：**算法如何知道自己身处对局的什么时间？**

A：传入参数tb中有属性是tick、tick_step，如果tick==0或者tick==tick_step，
说明目前正在处于刚刚开局，前者是对方发球，后者是自己发球后，对方刚接了过来。

Q：**各组分区的情况？**

A：我们采用SHA1散列得到了各组分区的方案如下：

```
[   ('E', ('VICTOR 端韵成', '048d67e83c3eebb45e5365841b77b57630c79f66')),
    ('E', ('DELTA 贾昊凝', '5087b26aa55ef219de39c019c7ab1db5cf36791f')),
    ('E', ('MIKE 王梦瑶', '64b38b02708559acf385db5db1ad187928e81010')),
    ('E', ('YANKEE 向汗青', '9aa6428daeaff43c6d974c9a11b4fb268c3355fc')),
    ('E', ('ECHO 蒋天骥', 'a86df20ef6eb6bc1928a9db1f0ce770d64af7526')),
    ('E', ('ROMEO 杨子珍', 'e07049f3f4be5e912711e01f580ae909a9d3fa57')),
    ('E', ('FOXTROT 李思彤', 'fbafc8a6c2e19176164d7233b16b96228826379d')),
    ('N', ('JULIET 朴健', '028e1fccd3a17ad9b6d60470430d68e1e0594c33')),
    ('N', ('OSCAR 吴宜谦', '3bf2b08e976a2fce94ec6b9b267cfd00126e51a5')),
    ('N', ('KILO 邵俊宁', '647b99c8082f0eb317c6af18889384b7f0462344')),
    ('N', ('UNIFORM 孟柳昳', '7fe2f6ec3cf022122f49d97c99e3885042eb89d2')),
    ('N', ('TANGO 周云帆', 'a4cdf25ef190b08a50116c7ff2ae0424f51898e5')),
    ('N', ('HOTEL 刘立洋', 'd1e56761ec1c8f848412b50fdef7978636541504')),
    ('N', ('X-RAY 裴召文', 'f0191877a1676d48034abba9a9e5db08db81f309')),
    ('S', ('ALPHA 常啸寅', '0910612cb1a6e719b5239c82e3c48ae42355227a')),
    ('S', ('BRAVO 陈宇枫', '644d3d92dac59fdc97d5246716e1bb75b6670165')),
    ('S', ('INDIA 闵靖涛', '7a0fb5a9638c57677970bd54a781226367d6b314')),
    ('S', ('QUEBEC 杨帆', 'a4c444a5a1b5c0a0c49d369b3ffa19b46ab53d57')),
    ('S', ('NOVEMBER 文家豪', 'bd95605cb56d25e20b7aa4fb468c2d78439c6616')),
    ('S', ('SIERRA 张影', 'ed142009fb940bc1576ad5f616ecb03c3ace5453')),
    ('W', ('WHISKEY 张容榕', '05a955efb6b49deebd8b8b8312da07d53503d7f0')),
    ('W', ('LIMA 陶天阳', '5894fb8d63b72b8a9baca57331d3eb08f2809e73')),
    ('W', ('GOLF 林荣', '798fdb7826c674756e2113870e5eaaba2ad2c439')),
    ('W', ('PAPA 徐晨雨', '9d7351896181b8d0106217cf4532e3b411363cfb')),
    ('W', ('ZULU 贺旎妮', 'bc880e24ca822e6c5077d36a27e9d1e4f88ece90')),
    ('W', ('CHARLIE 郭浩(地空)', 'e959fddf46cedf66f3babbb23969e0c848545ee9'))]
```

本结果计算的程序代码参见team.py。