# -*- coding: utf-8 -*-
u"""
Created on 2015-9-23

@author: cheng.li
"""

import datetime as dt
import numpy as np
import pandas as pd
from enum import IntEnum
from enum import unique
from AlgoTrading.Data.Data import DataFrameDataHandler
from AlgoTrading.Env import Settings
from DataAPI import api


@unique
class FreqType(IntEnum):
    MIN1 = 1
    MIN5 = 5
    EOD = 0


def route(freq):
    if freq == FreqType.MIN1:
        equity_api, future_api, index_api = api.GetEquityBarMin1, api.GetFutureBarMin1, api.GetIndexBarMin1
    elif freq == FreqType.MIN5:
        equity_api, future_api, index_api = api.GetEquityBarMin5, api.GetFutureBarMin5, api.GetIndexBarMin5
    elif freq == FreqType.EOD:
        equity_api, future_api, index_api = api.GetEquityBarEOD, api.GetFutureBarEOD, api.GetIndexBarEOD
    else:
        raise ValueError("Unknown bar type {0}".format(freq))

    return equity_api, future_api, index_api


class DXDataCenter(DataFrameDataHandler):

    _req_args = ['symbolList', 'startDate', 'endDate', 'freq']

    def __init__(self, **kwargs):
        super(DXDataCenter, self).__init__(kwargs['logger'], kwargs['symbolList'])
        self.fields = ['instrumentID', 'tradingDate', 'tradingTime', 'openPrice', 'highPrice', 'lowPrice', 'closePrice', 'volume']
        self.startDate = kwargs['startDate']
        self.endDate = kwargs['endDate']
        self._freq = kwargs['freq']

        if not Settings.usingCache:
            self.forceUpdate = True
        else:
            self.forceUpdate = False

        self._getMinutesBars(startDate=self.startDate.strftime("%Y-%m-%d"),
                             endDate=self.endDate.strftime("%Y-%m-%d"),
                             freq=self._freq)
        if kwargs['benchmark']:
            self._getBenchmarkData(kwargs['benchmark'],
                                   self.startDate.strftime("%Y-%m-%d"),
                                   self.endDate.strftime("%Y-%m-%d"))

    def _getMinutesBars(self, startDate, endDate, freq):

        self.logger.info("Starting load bars data from DX data center...")

        self.symbolData = {}

        equity_api, future_api, index_api = route(freq)

        equity_res = pd.DataFrame()
        future_res = pd.DataFrame()
        index_res = pd.DataFrame()

        if self.category['stocks']:
            equity_res = equity_api([s[:6] for s in self.category['stocks']],
                                    startDate,
                                    endDate,
                                    self.fields,
                                    baseDate='end',
                                    forceUpdate=self.forceUpdate)
        if self.category['futures']:
            future_res = future_api([f[:6] for f in self.category['futures']],
                                    startDate,
                                    endDate,
                                    self.fields,
                                    forceUpdate=self.forceUpdate)

        if self.category['indexes']:
            index_res = index_api([i[:6] for i in self.category['indexes']],
                                  startDate,
                                  endDate,
                                  self.fields,
                                  forceUpdate=self.forceUpdate)

        res = equity_res.append(future_res)
        res = res.append(index_res)

        timeIndexList = []
        dataList = []

        res = res[['securityID',
                   'tradingDate',
                   'tradingTime',
                   'openPrice',
                   'highPrice',
                   'lowPrice',
                   'closePrice',
                   'volume',
                   'instrumentID']]
        res = res.as_matrix()
        for row in res:
            s = row[0]
            if s not in self.symbolData:
                self.symbolData[s] = {}
                self.latestSymbolData[s] = []

            timeIndexList.append(row[1] + " " + row[2][:-1] + "+0000")
            dataList.append((s, {'open': row[3],
                                 'high': row[4],
                                 'low': row[5],
                                 'close': row[6],
                                 'volume': row[7]}))

        timeIndexList = np.array(timeIndexList, dtype='datetime64').astype(dt.datetime)
        for timeIndex, data in zip(timeIndexList, dataList):
            self.symbolData[data[0]][timeIndex] = data[1]

        self.dateIndex = np.unique(timeIndexList)
        self.dateIndex.sort()
        self.start = 0
        for i, s in enumerate(self.symbolList):
            if s not in self.symbolData:
                del self.symbolList[i]

        if not self.symbolList:
            raise ValueError("No any valid data for the whole universe")

        self.logger.info("Bars loading finished!")

    def _getBenchmarkData(self, indexID, startTimeStamp, endTimeStamp):

        self.logger.info("Starting load benchmark {0:s} daily bar data from DX data center...".format(indexID))

        indexData = api.GetIndexBarEOD(indexID[:6],
                                       startDate=startTimeStamp,
                                       endDate=endTimeStamp,
                                       forceUpdate=self.forceUpdate)
        indexData = indexData[['closePrice']]
        indexData.columns = ['close']
        indexData.index = pd.to_datetime(indexData.index.date)
        indexData['return'] = np.log(indexData['close'] / indexData['close'].shift(1))
        indexData = indexData.dropna()
        self.benchmarkData = indexData

        self.logger.info("Benchmark data loading finished!")
