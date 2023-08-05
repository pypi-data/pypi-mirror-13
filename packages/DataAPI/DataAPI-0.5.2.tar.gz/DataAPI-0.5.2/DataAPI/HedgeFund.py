# -*- coding: utf-8 -*-
u"""
Created on 2016-1-4

@author: cheng.li
"""

import pandas as pd
from DataAPI.Utilities import createEngine
from DataAPI.Utilities import NAMES_SETTINGS
from DataAPI.Utilities import list_to_str
from DataAPI.Utilities import enableCache
from DataAPI.Utilities import cleanColsForUnicode
from DataAPI.SqlExpressions import Condition


@enableCache
@cleanColsForUnicode
def GetHedgeFundInfo(instruments=None, field='*', firstInvestType=None, forceUpdate=True):
    u"""

    获取对冲基金基础信息

    :param instruments: 基金代码列表，例如：'XT1515141.XT'。默认为None，获取所有的基金信息
    :param field: 需要获取的字段类型，例如：['firstInvestType']，不填的话，默认获取所有字段；
                  可用的field包括：[instrumentID, fullName, firstInvestType, investScope,
                  maturityDate, advisory]
    :param firstInvestType: 需要获取的基金所属的投资类型列表，例如: [u'期货型']
    :param forceUpdate: 当为True时强制刷新数据，不使用缓存。默认为True
    :return: pandas.DataFrame
    """

    table_name = 'HEDGEFUND_DESC'

    engine = createEngine('hedge_funds')
    names_mapping = NAMES_SETTINGS[table_name]

    field = list_to_str(field, sep=u'', default_names=names_mapping)

    instruments_str = list_to_str(instruments)
    ins_condition = Condition(names_mapping[u"instrumentID"], instruments_str, u"in")

    first_invest_srt = list_to_str(firstInvestType)
    first_invest_condition = Condition(names_mapping[u"firstInvestType"], first_invest_srt, u"in")

    sql = u"select {0} from {1}".format(field, table_name)

    whole_condition = None
    if ins_condition:
        whole_condition = ins_condition & first_invest_condition
    elif first_invest_condition:
        whole_condition = first_invest_condition

    if whole_condition:
        sql += u" where " + whole_condition.__str__()
    data = pd.read_sql(sql, engine)
    return data


@enableCache
@cleanColsForUnicode
def GetHedgeFundPerf(instruments=None, field='*', forceUpdate=True, instrumentIDasCol=False):
    u"""

    获取对冲基金历史表现信息

    :param instruments: 基金代码列表，例如：'XT1515141.XT'。默认为None，获取所有基金历史表现
    :param field: 需要获取的字段类型，例如：['logRetAcc']，不填的话，默认获取所有字段；
                  可用的field包括：[tradingDate, instrumentID, navUnit, navAcc,
                  logRetUnit, logRetAcc]
    :param forceUpdate: 当为True时强制刷新数据，不使用缓存。默认为True
    :param instrumentIDasCol: 联合使用field以及instrumentIDs作为column的名字
    :return: pandas.DataFrame
    """
    engine = createEngine('hedge_funds')

    table_name = 'HEDGEFUND_PEF'
    names_mapping = NAMES_SETTINGS[table_name]

    field = list_to_str(field, sep=u'', default_names=names_mapping, forced_names=['tradingDate'])
    sql = u"select {0} from {1}".format(field, table_name)

    instruments_str = list_to_str(instruments)
    ins_condition = Condition(names_mapping[u"instrumentID"], instruments_str, u"in")

    whole_condition = None
    if ins_condition:
        whole_condition = ins_condition

    if whole_condition:
        sql += u" where " + whole_condition.__str__()

    data = pd.read_sql(sql, engine)
    data = setTimeStamp(data, instrumentIDasCol)
    return data


@enableCache
@cleanColsForUnicode
def GetHedgeFundPool(field='*', refDate=None, forceUpdate=True):
    u"""

    获取指定日期下，基金备选池的信息

    :param field: 需要获取的字段类型，例如：['logRetAcc']，不填的话，默认获取所有字段；
                  可用的field包括：[tradingDate, instrumentID, navUnit, navAcc,
                  logRetUnit, logRetAcc]
    :param refDate: 指定日期，将查询范围限制于当日在基金备选池中的基金，格式为：YYYY-MM-DD；
                    不填的话，默认查询最新的备选池信息
    :param forceUpdate: 当为True时强制刷新数据，不使用缓存。默认为True
    :return: pandas.DataFrame
    """
    engine = createEngine('hedge_funds')
    table_name = 'HEDGEFUND_POOL'
    names_mapping = NAMES_SETTINGS[table_name]

    ref_condition = None
    if refDate:
        ref_condition = Condition(names_mapping[u'eventDate'], refDate.replace(u'-', u''), u"<=")

    sql = u'select * from {0}'.format(table_name)
    if ref_condition:
        sql += u" where " + ref_condition.__str__()

    data = pd.read_sql(sql, engine)
    data = data.groupby(names_mapping['instrumentID']).last()
    data = data[data.eventType == 'A'][['eventDate']]

    # get the detail info of the instruments
    if field != '*':
        if isinstance(field, str):
            field = [field]
        if 'instrumentID' not in field:
            field.append('instrumentID')

    info_data = GetHedgeFundInfo(list(data.index.values), field=field)
    data = pd.merge(data, info_data, left_index=True, right_on='instrumentID')
    return data


def setTimeStamp(data, instrumentIDasCol):
    data['tradingDate'] = pd.to_datetime(data['tradingDate'], format='%Y%m%d')
    if instrumentIDasCol:
        data.set_index(['tradingDate', 'instrumentID'], inplace=True, verify_integrity=True)
        data = data.unstack(level=-1)
    else:
        data.set_index('tradingDate', inplace=True)
    return data
