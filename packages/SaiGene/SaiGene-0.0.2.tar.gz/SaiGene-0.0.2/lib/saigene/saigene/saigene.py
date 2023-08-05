#!/usr/bin/env python
# -*- coding: utf-8 -*-

from datetime import datetime, date, time


class NonvalidYearException(Exception):  # Exceptionを継承
    def __init__(self, value):
        self.value = value

    def __str__(self):
        return repr(self.value)


class SaiGene:
    def __init__(self, age=17, lang="en"):
        """
        初期化
        :type target_age: 年齢
        :type lang:言語
        """
        self.target_age = age
        self.lang = lang

    @property
    def target_age(self):
        '''target_age property'''
        return self._target_age

    @target_age.setter
    def target_age(self, value):
        self._target_age = max(value, 0)

    @property
    def lang(self):
        '''lang property'''
        return self._lang

    @lang.setter
    def lang(self, value):
        self._lang = value.lower()

    def calculate_human_age(self, born):
        """
        普通に人間的な年齢を計算する
        :param born: date型の日付
        :return: 人間的な年齢
        """
        today = date.today()
        try:
            birthday = born.replace(year=today.year)
        except ValueError:  # raised when birth date is February 29 and the current year is not a leap year
            birthday = born.replace(year=today.year, month=born.month + 1, day=1)
        if birthday > today:
            return today.year - born.year - 1
        else:
            return today.year - born.year

    def __calc_month(self, born):
        """
        何ヶ月か
        :param born:
        :return: ○ヶ月
        """
        today = date.today()
        try:
            birthday = born.replace(year=today.year)
        except ValueError:  # raised when birth date is February 29 and the current year is not a leap year
            birthday = born.replace(year=today.year, month=born.month + 1, day=1)
        if birthday > today:
            return ((today.year - born.year - 1) - self.target_age) * 12
        else:
            return ((today.year - born.year) - self.target_age) * 12

    def _format1(self, month):
        if self.lang == "ja":
            return "と{month}ヶ月".format(month=month)
        elif self.lang == "kr":
            return "와{month}개월".format(month=month)
        elif self.lang == "fr":
            return " et {month} mois".format(month=month)
        elif self.lang == "vi":
            return " và {month} tháng".format(month=month)

        month_str = "month"
        if month > 1:
            month_str += "s"
        return " and {month} {s}".format(month=month, s=month_str)

    def _format2(self, age):
        if self.lang == "ja":
            return "{age}歳".format(age=age)
        elif self.lang == "kr":
            return "{age}세".format(age=age)
        elif self.lang == "fr":
            age_str = "an"
            if age > 1:
                age_str += "s"
            return "{age} {s}".format(age=age, s=age_str)
        elif self.lang == "vi":
            return "{age} năm".format(age=age)

        age_str = "year"
        if age > 1:
            age_str += "s"
        return "{age} {s}".format(age=age, s=age_str)

    def calculate(self, born):
        """
        年齢を計算する
        :param born:
        :return: 年齢または生年月日
        """
        if type(born) == int:
            age = max(born, self.target_age)
            msg = ""
            if born > age:
                months = (born - age) * 12
                msg = self._format1(months)
            return self._format2(age) + msg
        else:
            msg = ""
            months = self.__calc_month(born)
            if months > 0:
                msg = self._format1(months)
            # 年齢計算する
            return self._format2(self.target_age) + msg
