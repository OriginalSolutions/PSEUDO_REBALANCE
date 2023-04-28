#!/usr/bin/env python3.8
#
import pandas as pd
from datetime import datetime
import copy
import requests    

BASE_URL = "https://api.gateio.ws"
CONTEX = "/api/v4"
HEADERS = {'Accept': 'application/json', 'Content-Type': 'application/json'}
URL = '/spot/candlesticks'
SHORT = 'currency_pair=BTC5S_USDT&interval=5m&limit=1000'
LONG = 'currency_pair=BTC5L_USDT&interval=5m&limit=1000'
        
        
#####################################################################

class functions:
    def __init__(self, BASE_URL, CONTEX, HEADERS, URL, SHORT, LONG):
        self.BASE_URL = BASE_URL
        self.CONTEX = CONTEX
        self.HEADERS = HEADERS
        self.URL = URL,
        self.SHORT = SHORT
        self.LONG = LONG
    @staticmethod
    def loading(BASE_URL, CONTEX, HEADERS, URL, SHORT, LONG):
        s = requests.request('GET', BASE_URL + CONTEX + URL + "?" + SHORT, headers=HEADERS)
        s = s.json()
        l = requests.request('GET', BASE_URL + CONTEX + URL + "?" + LONG, headers=HEADERS)
        l = l.json()
        return [s, l]
    @staticmethod
    def close_gate(r):
        close_long =list()
        index_time_long = list()
        for kline in r:
            close_long.append(float(kline[2])) 
            time_long = datetime.fromtimestamp(int(kline[0])).strftime("%Y-%m-%d %H:%M:%S")   
            index_time_long.append(time_long)   #  time as  int()
        return [close_long,  index_time_long]
    @staticmethod
    def data_frame(series, time, columns):
        i=0
        ts = list()
        for t in time:
            ts.append(t)
            ts.append(series[i])
            i += 1
        close = pd.Series(series)
        close.index = pd.to_datetime(time)    
        data_f = pd.DataFrame (close, columns = [columns])
        return data_f
    # #####################################################################
    @staticmethod
    def elimination_of_the_split(data):
        i=0
        while i < len(data)-1:
            div = data.iloc[i+1] / data.iloc[i]
            if div['Long'] > 80:
                print(i+1)
                print(data['Long'][i+1:]/100)
                data['Long'][i+1:] = data['Long'][i+1:]/100
            elif div['Short'] > 80:
                print(i+1)
                print(data['Short'][i+1:]/100)
                data['Short'][i+1:] = data['Short'][i+1:]/100
            i += 1
        return data
    @staticmethod
    def len_while(len_lp, len_sp):
        if len_lp >= len_sp:
            len_w = len_lp
        else:
            len_w = len_sp
        return len_w
    @staticmethod
    def first_profit_date_of_the_token_short(data, Short_Profit, p, t):
        if len(data['Short_Profit'][data['Short_Profit'] > p][t: ]) > int(1):   
            # PROFIT of the second token above a certain threshold
            data_sh =  data['Short_Profit'][data['Short_Profit'] > p][t: ]   
            # The first time the profit value exceeds a certain threshold
            ind_sh = pd.to_datetime(data[data['Short_Profit'] > p][t: ].index)    
        else: 
            ind_sh = {0: pd.to_datetime(str(2090)), 1: pd.to_datetime(str(2095))} 
            data_sh = {0: 0, 1: 0}
        return [data_sh, ind_sh]
    @staticmethod
    def first_profit_date_of_the_token_long(data, Long_Profit, p, t):
        if len(data['Long_Profit'][data['Long_Profit'] > p][t: ]) > int(1):
            data_lo =  data['Long_Profit'][data['Long_Profit'] > p][t: ] 
            ind_lo = pd.to_datetime(data[data['Long_Profit'] > p][t: ].index) 
        else: 
            ind_lo = {0: pd.to_datetime(str(2090)), 1: pd.to_datetime(str(2095))} 
            data_lo = {0: 0, 1: 0}
        return [data_lo, ind_lo]
    @staticmethod
    def upper_and_lower_standard_deviation(data, period, multiplier):
        upper_std = data.rolling(period).mean()+data.rolling(period).std()*multiplier
        lower_std = data.rolling(period).mean()-data.rolling(period).std()*multiplier
        return [upper_std, lower_std]
# END