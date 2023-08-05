#!/usr/bin/env python
# -*- coding: utf-8 -*-

import unittest
from lib.saigene.saigene import SaiGene

from datetime import date


class SaiGeneTest(unittest.TestCase):
    def setUp(self):
        self.mc = SaiGene(lang="vi")

    def test_human_age(self):
        """
        人間の年
        """
        born = date(1984, 1, 4)
        res = self.mc.calculate_human_age(born)
        self.assertEqual(res, 32)

    def test_age(self):
        """
        年齢計算
        """
        born = date(1984, 1, 4)
        res = self.mc.calculate(born)
        print(res)
        self.assertEqual(res, "17歳と180ヶ月")

if __name__ == '__main__':
    unittest.main()
