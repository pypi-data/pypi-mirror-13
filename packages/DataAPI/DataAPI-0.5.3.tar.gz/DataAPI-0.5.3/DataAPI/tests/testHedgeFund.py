# -*- coding: utf-8 -*-
u"""
Created on 2016-1-5

@author: cheng.li
"""

import unittest
from DataAPI import api


@unittest.skip("skipping tests for hedge fund related stuff.")
class TestHedgeFund(unittest.TestCase):

    def test_hedge_fund_info(self):
        data = api.GetHedgeFundInfo()
        self.assertTrue(len(data) > 1)

    def test_hedge_fund_info_with_specific_first_invest(self):
        data = api.GetHedgeFundInfo(firstInvestType=u'股票型')
        first_invest_types = data.firstInvestType.values
        for ftype in first_invest_types:
            self.assertEqual(ftype, u'股票型')

    def test_hedge_fund_info_with_wrong_field(self):
        with self.assertRaises(ValueError):
            _ = api.GetHedgeFundInfo(field='listDate')

    def test_hedge_fund_info_with_specific_field(self):
        data = api.GetHedgeFundInfo(field='fullName')
        self.assertTrue('fullName' in data)
        self.assertTrue('instrumentID' not in data)

    def test_hedge_fund_perf_with_specific_instrument(self):
        data = api.GetHedgeFundPerf('XT1520453.XT')
        instruments = data.instrumentID.unique()
        self.assertEqual(len(instruments), 1)
        self.assertEqual(instruments[0], u'XT1520453.XT')

    def test_hedge_fund_perf_with_wrong_field(self):
        with self.assertRaises(ValueError):
            _ = api.GetHedgeFundPerf(field='listDate')

    def test_hedge_fund_perf_with_specific_field(self):
        data = api.GetHedgeFundPerf(field='navUnit')
        self.assertTrue('navUnit' in data)
        self.assertTrue('navAcc' not in data)
