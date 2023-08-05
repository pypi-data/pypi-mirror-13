# -*- coding: utf-8 -*-
u"""
Created on 2015-11-12

@author: cheng.li, weijun.shen
"""

import os
import sys
import tushare as ts
import sqlite3
import hashlib
import inspect
import types
from collections import OrderedDict
from enum import IntEnum
import decorator
import pandas as pd
import pymssql
import warnings

warnings.filterwarnings('ignore', category=pd.io.pytables.PerformanceWarning)

SH_INDEX_MAPPINGS = \
    {
        '000001': '999999',
        '000002': '999998',
        '000003': '999997',
        '000004': '999996',
        '000005': '999995',
        '000006': '999994',
        '000007': '999993',
        '000008': '999992',
        '000010': '999991',
        '000011': '999990',
        '000012': '999989',
        '000013': '999988',
        '000016': '999987',
        '000015': '999986',
        '000300': '000300',
    }

REV_SH_INDEX_MAPPINGS = dict((v, k) for k, v in SH_INDEX_MAPPINGS.items())

DB_SETTINGS = \
    {
        "datacenter_eqy":
            {
                'user': 'test',
                'pwd': '12345678',
                'host': '10.63.6.84',
                'timeout': 60
            },
        "datacenter_eqy_new":
            {
                'user': 'test',
                'pwd': '12345678',
                'host': '10.63.6.84',
                'timeout': 60
            },
        "datacenter_futures":
            {
                'user': 'test',
                'pwd': '12345678',
                'host': '10.63.6.84',
                'timeout': 60
            },
        "WindDB":
            {
                'user': 'Intern',
                'pwd': 'Abc12345678!',
                'host': '10.63.6.100',
                'timeout': 60
            },
        "hedge_funds":
            {
                'file': 'd:/hedge_funds.db'
            }
    }

NAMES_SETTINGS = \
    {
        "market_data":
            {
                u'productID': u'productID',
                u'instrumentID': u'instrumentID',
                u'tradingDate': u'tradingDate',
                u'tradingTime': u'tradingTime',
                u'openPrice': u'openPrice',
                u'highPrice': u'highPrice',
                u'lowPrice': u'lowPrice',
                u'closePrice': u'closePrice',
                u'volume': u'volume',
                u'turnover': u'turnover',
                u'matchItems': u'matchItems'
            },
        "equity_eod":
            {
                u'productID': u'productID',
                u'instrumentID': u'S_INFO_WINDCODE',
                u'tradingDate': u'TRADE_DT',
                u'tradingTime': u'tradingTime',
                u'openPrice': u'S_DQ_OPEN',
                u'highPrice': u'S_DQ_HIGH',
                u'lowPrice': u'S_DQ_LOW',
                u'closePrice': u'S_DQ_CLOSE',
                u'volume': u'S_DQ_VOLUME',
                u'turnover': u'S_DQ_AMOUNT'
            },
        "index_eod":
            {
                u'productID': u'productID',
                u'instrumentID': u'S_INFO_WINDCODE',
                u'tradingDate': u'TRADE_DT',
                u'tradingTime': u'tradingTime',
                u'openPrice': u'S_DQ_OPEN',
                u'highPrice': u'S_DQ_HIGH',
                u'lowPrice': u'S_DQ_LOW',
                u'closePrice': u'S_DQ_CLOSE',
                u'volume': u'S_DQ_VOLUME',
                u'turnover': u'S_DQ_AMOUNT'
            },
        "future_info":
            {
                u'instrumentID': u'S_INFO_CODE',
                u'windCode': u'S_INFO_WINDCODE',
                u'market': u'S_INFO_EXCHMARKET',
                u'enName': u'S_INFO_ENAME',
                u'cnName': u'S_INFO_NAME'
            },
        "equity_info":
            {
                u'windCode': u'S_INFO_WINDCODE',
                u'instrumentID': u'S_INFO_CODE',
                u'cnName': u'S_INFO_NAME',
                u'cnFullName': u'S_INFO_COMPNAME',
                u'enFullName': u'S_INFO_COMPNAMEENG',
                u'isinCode': u'S_INFO_ISINCODE',
                u'exchange': u'S_INFO_EXCHMARKET',
                u'listBoard': u'S_INFO_LISTBOARD',
                u'listBoardName': u'S_INFO_LISTBOARDNAME',
                u'listDate': u'S_INFO_LISTDATE',
                u'delistDate': u'S_INFO_DELISTDATE'
            },
        "index_members":
            {
                u'instrumentID': u'instrumentID',
                u'windCode': u'S_INFO_WINDCODE',
                u'conInstrumentID': u'conInstrumentID',
                u'conWindCode': u'S_CON_WINDCODE',
                u'inDate': u'S_CON_INDATE',
                u'outDate': u'S_CON_OUTDATE',
                u'conSecurityID': u'conSecurityID'
            },
        "mutual_fund_min5":
            {
                u'productID': u'productID',
                u'instrumentID': u'instrumentID',
                u'tradingDate': u'tradingDate',
                u'tradingTime': u'tradingTime',
                u'openPrice': u'openPrice',
                u'highPrice': u'highPrice',
                u'lowPrice': u'lowPrice',
                u'closePrice': u'closePrice',
                u'volume': u'volume',
                u'turnover': u'turnover'
            },
        "HEDGEFUND_DESC":
            {
                u'instrumentID': u'instrumentID',
                u'fullName': u'fullName',
                u'firstInvestType': u'firstInvestType',
                u'investScope': u'investScope',
                u'maturityDate': u'maturityDate',
                u'advisory': u'advisory'
            },
        "HEDGEFUND_PEF":
            {
                u'tradingDate': u'tradingDate',
                u'instrumentID': u'instrumentID',
                u'navUnit': u'navUnit',
                u'navAcc': u'navAcc',
                u'logRetUnit': u'logRetUnit',
                u'logRetAcc': u'logRetAcc'
            },
        "HEDGEFUND_POOL":
            {
                u'eventDate': u'eventDate',
                u'eventType': u'eventType',
                u'instrumentID': u'instrumentID'
            },
        "theme_info":
            {
                u'themeID': u'themeID',
                u'themeName': u'themeName',
                u'isActive': u'isActive',
                u'insertTime': u'insertTime',
                u'updateTime': u'updateTime'
            },
        "theme_hotness":
            {
                u'themeID': u'themeID',
                u'themeName': u'themeName',
                u'date': 'statisticsDate',
                u'newsNum': u'newsNum',
                u'newsNumPercent': u'newsNumPercent'
            },
        "stocks_by_theme":
            {
                u'themeID': u'themeID',
                u'themeName': u'themeName',
                u'instrumentID': u'secID',
                u'cnName': u'secShortName',
                u'exchangeName': u'exchangeName',
                u'score': u'returnScore'
            },
        "active_theme_related_stocks":
            {
                u'themeID': u'themeID',
                u'themeName': u'themeName',
                u'instrumentID': u'secID',
                u'cnName': u'secShortName',
                u'date': u'date',
                u'themeHotness': u'themeHotness',
                u'score': u'score'
            }
    }


@decorator.decorator
def enableCache(f, *args, **kwargs):
    u"""

    装饰器，为返回值为pandas.DataFrame的函数提供本地缓存功能

    :param f: 返回值为pandas.DataFrame的函数
    :param args: 准备传递给f的位置参数
    :param kwargs: 准备传递给f的关键字参数
    :return: pandas.DataFrame
    """
    folder = '.dstore'

    argSpec = inspect.getargspec(f)
    argDict = argSpec._asdict()

    names = argDict['args']

    try:
        chunksize = args[names.index("chunksize")]
        if chunksize is not None:
            return f(*args, **kwargs)
    except ValueError:
        pass

    try:
        forceUpdate = args[names.index("forceUpdate")]
        if forceUpdate:
            return f(*args, **kwargs)
    except ValueError:
        pass

    if not os.path.isdir(folder):
        try:
            os.mkdir(folder)
        except OSError:
            print("can't make folder '" + folder + "' for tmp store. Cache mechanism is disabled ")

    if os.path.isdir(folder):

        callerSignature = OrderedDict()
        callerSignature['name'] = f.__name__
        callerSignature['args'] = args
        callerSignature['kwargs'] = kwargs
        callerSignature = callerSignature.__str__()
        uniqueID = hashlib.sha224(callerSignature.encode('utf8')).hexdigest()
        filePath = os.path.join(folder, uniqueID + ".hdf")

        if os.path.exists(filePath):
            print(callerSignature + " is reading from cach " + os.path.abspath(filePath) + "... ")
            data = pd.read_hdf(filePath, key="df")
            data.sortlevel(level=0, axis=1, inplace=True)
        else:
            data = f(*args, **kwargs)
            if not data.empty:
                data.to_hdf(filePath, key='df', mode='w', format='fixed')
        return data
    else:
        return f(*args, **kwargs)


@decorator.decorator
def cleanColsForUnicode(f, *args, **kwargs):
    u"""

    装饰器，为返回值为pandas.DataFrame的函数进行中文编码的转换

    :param f: 返回值为pandas.DataFrame的函数
    :param args: 准备传递给f的位置参数
    :param kwargs: 准备传递给f的关键字参数
    :return: pandas.DataFrame
    """
    data = f(*args, **kwargs)
    if sys.version_info > (3, 0, 0):
        return data
    else:
        # we have to check encoding issue in python 2
        if not isinstance(data, types.GeneratorType) and not data.empty:
            dtypes = data.apply(lambda x: pd.lib.infer_dtype(x.values))
            for col in dtypes[dtypes == 'unicode'].index:
                data[col] = data[col]
    return data


def categorizeSymbols(symbolList):

    lowSymbols = [s.lower() for s in symbolList]

    stocks = []
    futures = []
    indexes = []

    for s in lowSymbols:
        if s.endswith('xshg') or s.endswith('xshe'):
            stocks.append(s)
        elif s.endswith('zicn'):
            indexes.append(s)
        else:
            s_com = s.split('.')
            if len(s_com) < 2:
                raise ValueError("Unknown securitie name {0}. Security names without"
                                 " exchange suffix is not allowed in general data fetching".format(s))
            futures.append(s_com[0])
    return {'stocks': stocks, 'futures': futures, 'indexes': indexes}


def createEngine(_DB):
    global DB_SETTINGS
    setting = DB_SETTINGS[_DB]
    if 'user' in setting:
        return pymssql.connect(host=setting['host'],
                               user=setting['user'],
                               password=setting['pwd'],
                               database=_DB,
                               timeout=setting['timeout'],
                               charset='utf8')
    elif 'file' in setting:
        return sqlite3.connect(setting['file'])


def field_names_mapping(items, names_mapping, forced_names=None):

    if sys.version_info > (3, 0, 0):
        if isinstance(items, str):
            items = [items]
    else:
        if isinstance(items, unicode) or isinstance(items, str):
            items = [items]

    if names_mapping:
        new_items = []
        if items == [u'*']:
            for key in names_mapping:
                new_items.append((names_mapping[key], key))
        else:
            for item in items:
                try:
                    new_items.append((names_mapping[item], item))
                except KeyError:
                    pass

            if not new_items:
                raise ValueError("Unknown field names {0}. "
                                 "The only available names are {1}".format(items,
                                                                           names_mapping.keys()))
            if forced_names:
                for item in forced_names:
                    new_items.append((names_mapping[item] , item))

        items = new_items

    return items


def list_to_str(items, sep=u"'",
                default_names=None,
                forced_names=None,
                limit_size=None,
                prefix='',
                suffix=''):
    info_str = None
    if items is not None:
        items = field_names_mapping(items, default_names, forced_names)
        if isinstance(items[0], tuple):
            items = [item[0] + u" as " + item[1] for item in items]
        info_str = u",".join([sep + prefix + item[:limit_size] + suffix + sep for item in items])

    return info_str


###################################
# 通联数据接口
###################################

class SubjectWrapper:

    def __init__(self):
        self.subject = ts.Subject()

    def ThemesContent(self, *args, **kwargs):
        try:
            return self.subject.ThemesContent(*args, **kwargs)
        except TypeError:
            raise ValueError('Please set the token for DataYes (using api.Settings.set_tocken(...)')

    def ThemesHeat(self, *args, **kwargs):
        try:
            return self.subject.ThemesHeat(*args, **kwargs)
        except TypeError:
            raise ValueError('Please set the token for DataYes (using api.Settings.set_tocken(...)')

    def TickersByThemes(self, *args, **kwargs):
        try:
            return self.subject.TickersByThemes(*args, **kwargs)
        except TypeError:
            raise ValueError('Please set the token for DataYes (using api.Settings.set_tocken(...)')

    def ThemesContent(self, *args, **kwargs):
        try:
            return self.subject.ThemesContent(*args, **kwargs)
        except TypeError:
            raise ValueError('Please set the token for DataYes (using api.Settings.set_tocken(...)')


def str_to_list(names):

    if sys.version_info > (3, 0, 0):
        if isinstance(names, str):
            names = [names]
    else:
        if isinstance(names, str) or isinstance(names, unicode):
            names = [names]
    return names


class MarketWrapper:

    def __init__(self):
        self.market = ts.Market()

    def IndustryTickRTSnapshot(self, *args, **kwargs):
        try:
            return self.market.IndustryTickRTSnapshot(*args, **kwargs)
        except TypeError:
            raise ValueError('Please set the token for DataYes (using api.Settings.set_tocken(...)')


class ASSET_TYPE(IntEnum):
    EQUITY = 1
    FUTURES = 2
    INDEX = 3
    OPTION = 4
    MUTUALFUND = 5


class BAR_TYPE(IntEnum):
    MIN1 = 1
    MIN5 = 2
    EOD = 3


def _generateSecurityID(data, aType):
    if aType == ASSET_TYPE.INDEX:
        securityIDs = data.apply(lambda x: x.lower() + '.zicn')
    elif aType == ASSET_TYPE.FUTURES:
        securityIDs = data.apply(lambda x: x.lower() + '.cffex')
    elif aType == ASSET_TYPE.EQUITY:
        securityIDs = data.apply(lambda x: x.lower() + '.xshg' if x.startswith('6') else x.lower() + '.xshe')
    elif aType == ASSET_TYPE.MUTUALFUND:
        securityIDs = data.apply(lambda x: x.lower() + '.xshg' if x.startswith('51') else x.lower() + '.xshe')

    return securityIDs


def _setTimeStamp(data, bType, instrumentIDasCol):
    if bType != BAR_TYPE.EOD:
        data['timeStamp'] = data['tradingDate'] + ' ' + data['tradingTime']
        data['timeStamp'] = pd.to_datetime(data['timeStamp'], format="%Y-%m-%d %H:%M:%S.%f")
    else:
        data['timeStamp'] = data['tradingDate']
        data['timeStamp'] = pd.to_datetime(data['timeStamp'], format="%Y-%m-%d")

    if instrumentIDasCol:
        data.drop(['tradingDate', 'tradingTime'], axis=1, inplace=True)
        if 'tradingMilliSec' in data:
            data.drop('tradingMilliSec', axis=1, inplace=True)
        data.set_index(['timeStamp', 'instrumentID'], inplace=True, verify_integrity=True)
        data = data.unstack(level=-1)
    else:
        data.set_index('timeStamp', inplace=True)
    return data


class TSSettingsFactory:

    def __init__(self):
        self.theme_list = pd.DataFrame()

    @property
    def global_theme_list(self):
        if self.theme_list.empty:
            subject = ts.Subject()
            self.theme_list = subject.ThemesContent(field='themeName,themeID')
            self.theme_list.themeName = self.theme_list.themeName.str.decode('utf8')
        return self.theme_list

    def set_token(self, token=None):
        if not token:
            ts.set_token('2bfc4b3b06efa5d8bba2ab9ef83b5d61f1c3887834de729b60eec9f13e1d4df8')
        else:
            ts.set_token(token)

    def subject(self):
        try:
            return SubjectWrapper()
        except TypeError:
            raise ValueError('Please set the token for DataYes (using api.Settings.set_tocken(...)')

    def market(self):
        try:
            return MarketWrapper()
        except TypeError:
            raise ValueError('Please set the token for DataYes (using api.Settings.set_tocken(...)')


Settings = TSSettingsFactory()
