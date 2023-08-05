# -*- coding: utf-8 -*-
from 臺灣言語工具.解析整理.拆文分析器 import 拆文分析器


class 斷詞結構化工具:
    _分析器 = 拆文分析器()

    @classmethod
    def 斷詞轉章物件(cls, 斷詞結果):
        章物件 = cls._分析器.建立章物件('')
        for 一逝 in 斷詞結果:
            句物件 = cls.斷詞轉句物件(一逝)
            章物件.內底句.append(句物件)
        return 章物件

    @classmethod
    def 斷詞轉句物件(cls, 斷詞結果):
        句物件 = cls._分析器.建立句物件('')
        for 半句 in 斷詞結果:
            組物件 = cls.斷詞轉組物件(半句)
            集物件 = cls._分析器.建立集物件('')
            集物件.內底組.append(組物件)
            句物件.內底集.append(集物件)
        return 句物件

    @classmethod
    def 斷詞轉組物件(cls, 斷詞結果):
        組物件 = cls._分析器.建立組物件('')
        for 詞, 詞性 in 斷詞結果:
            詞物件 = cls._分析器.建立詞物件(詞)
            詞物件.屬性 = {'詞性': 詞性}
            組物件.內底詞.append(詞物件)
        return 組物件
