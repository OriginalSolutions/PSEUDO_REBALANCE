#!/usr/bin/env python3.8
#
import pandas as pd
import matplotlib.pyplot as plt
from datetime import datetime
from datetime import timedelta
from time import time
from time import sleep
import copy
import requests    
from functions_pseudo_rebalance import functions
from functions_pseudo_rebalance import BASE_URL, CONTEX, HEADERS, URL, SHORT, LONG

#######################################################################################
#
# LOADING AND CONVERTING DATA TO PANDAS FORMAT
#
#######################################################################################
f = functions(BASE_URL, CONTEX, HEADERS, URL, SHORT , LONG)
s, l = f.loading(BASE_URL, CONTEX, HEADERS, URL, SHORT , LONG)

close_l, index_time_l = f.close_gate(l)
close_s, index_time_s = f.close_gate(s)

data_long = f.data_frame(close_l, index_time_l, "Long")
data_short = f.data_frame(close_s, index_time_s, "Short")
data = copy.deepcopy(data_long)
data['Short'] = copy.deepcopy(data_short)
print(data)

data = f.elimination_of_the_split(data)
data['Long_quotient'] = data['Long'] / data['Long'][0]  
data['Short_quotient'] = data['Short'] / data['Short'][0]
data['The_first_sum_of_the_quotient'] = data['Long_quotient'] + data['Short_quotient'] 

## if profit long occurs for the first time
## (get the time index of this gain and) calculate since then: quotient short * (old quotient short + gain long) 
data['Long_Profit'] = copy.deepcopy(data['Long_quotient'])  
data['Short_Profit'] = copy.deepcopy(data['Short_quotient'])


#######################################################################################
#
# DECLARING PARAMETERS
#
#######################################################################################
profitability = float(1.02)    ## Profitability expressed as a ratio of the value of
part_of_profit = float(0.08)   ## Value  > 1.0  only for the experiment.  Denotes the opposite direction to "balancing"
commission = 0.001
i = 1
iteator_data = int(0)
time_iterator = int(0)
minutes=5

len_lp = len(data.loc[(data['Long_quotient'] > profitability), 'Long_Profit'])
len_sp = len(data.loc[(data['Short_quotient'] > profitability), 'Short_Profit'])
len_w = f.len_while(len_lp, len_sp) 

data.loc[(data['Long_quotient'] >= profitability ), 'Long_Profit'] = (data['Long_quotient'] - int(1))   
data.loc[(data['Long_quotient'] < profitability ), 'Long_Profit'] = 0.0
data.loc[(data['Short_quotient'] >= profitability ), 'Short_Profit'] = (data['Short_quotient'] - int(1)) 
data.loc[(data['Short_quotient'] < profitability ), 'Short_Profit'] = 0.0


#######################################################################################
#
# BACKTESTING - REBALANCING
#
#######################################################################################
while i < len_w:  
    #
    data_s, ind_s = f.first_profit_date_of_the_token_short(data, 'Short_Profit', profitability - 1, time_iterator)
    data_l, ind_l = f.first_profit_date_of_the_token_long(data, 'Long_Profit', profitability - 1, time_iterator)
        #
    if len(ind_s) <= iteator_data and len(ind_l) <= iteator_data:
        print("_1_")
        ind_s  = ind_s[len(ind_s) -1 ]
        data_s = data_s[len(data_s)-1]
        ind_l  = ind_l[len(ind_l) -1 ]
        data_l = data_l[len(data_l)-1]
        #
    elif len(ind_s) <= iteator_data and len(ind_l) > iteator_data:
        print("_2_")
        ind_s  = ind_s[len(ind_s) -1 ] 
        data_s = data_s[len(data_s)-1]
        ind_l  = ind_l[iteator_data] 
        data_l = data_l[iteator_data]
        #
    elif  len(ind_l) <= iteator_data and len(ind_s) > iteator_data:
        print("_3_")
        ind_l  = ind_l[len(ind_l) -1 ]
        data_l = data_l[len(data_l)-1]
        ind_s  = ind_s[iteator_data] 
        data_s = data_s[iteator_data]
        #
    else:
        ind_l  = ind_l[iteator_data] 
        data_l = data_l[iteator_data]
        ind_s  = ind_s[iteator_data] 
        data_s = data_s[iteator_data]
        #
    print("We are beginning the process of back-testing pseudo rebalancing")
    ######################################################
    if ind_s < ind_l:       
        ## Increase the quotient value of a token that incurs losses by adding a portion of the generated profit from a token that makes a profit.
        print(ind_s) ## token time that generates profit
        part_of_profit_short  = (data_s * part_of_profit) * (1 - commission)   # SELL
        data['Long_quotient'][ind_s: ][0] = data['Long_quotient'][ind_s: ][0] + (part_of_profit_short * (1-commission))   # BUY
        print(data['Long_quotient'][ind_s: ][0])
        ## Update the quotient of the losing token 
        data['Long_quotient'][ind_s: ] = (data['Long'][ind_s: ] / data['Long'][ind_s: ][0]) * data['Long_quotient'][ind_s: ][0]
        #
        ## Diminishing the value of the gaining token. Diminishing a portion of "one's", "own" profit.
        data['Short_quotient'][ind_s: ][0] = data['Short_quotient'][ind_s: ][0] - (data_s * part_of_profit)
        data['Short_quotient'][ind_s: ] = (data['Short'][ind_s: ] / data['Short'][ind_s: ][0]) * data['Short_quotient'][ind_s: ][0]
        #
        ## Profit update
        t = ind_s + timedelta(minutes=minutes)
        ## Token, that loses
        data['Long_Profit'][t: ] =  data['Long'][t: ] / data['Long'][ind_s]
        print(data['Long_Profit'][ind_s: ])
        ## Token, that gains
        data['Short_Profit'][ind_s] =  data_s  
        data['Short_Profit'][t: ] =  data['Short'][t: ] / data['Short'][ind_s]
        print(data['Short_Profit'][ind_s: ])
        #
        len_lp = len(data.loc[(data['Long_quotient'] > profitability ), 'Long_Profit'])
        len_sp = len(data.loc[(data['Short_quotient'] > profitability ), 'Short_Profit'])
        len_w = f.len_while(len_lp, len_sp) 
        print(ind_s)
        print(ind_l)
        #
    elif ind_l < ind_s:  
        ## Increase the quotient value of a token that incurs losses by adding a portion of the generated profit from a token that makes a profit.
        print(ind_l) ## token time that generates profit
        part_of_profit_long  = (data_l * part_of_profit) * (1 - commission)   # SELL
        data['Short_quotient'][ind_l: ][0] = data['Short_quotient'][ind_l: ][0] + (part_of_profit_long * (1-commission))   # BUY
        print(data['Short_quotient'][ind_l: ][0])  
        data['Short_quotient'][ind_l: ] = (data['Short'][ind_l: ] / data['Short'][ind_l: ][0]) * data['Short_quotient'][ind_l: ][0]  
        #
        ## Diminishing the value of the gaining token. Diminishing a portion of "one's", "own" profit.
        data['Long_quotient'][ind_l: ][0] = data['Long_quotient'][ind_l: ][0] - ( data_l * part_of_profit)
        data['Long_quotient'][ind_l: ] = (data['Long'][ind_l: ] / data['Long'][ind_l: ][0]) * data['Long_quotient'][ind_l: ][0]
        #
        ## Profit update
        t = ind_l + timedelta(minutes=minutes)
        ## Token, that loses
        data['Short_Profit'][t: ] = data['Short'][t: ] / data['Short'][ind_l]
        print(data['Short_Profit'][t: ])
        ## Token, that gains
        data['Long_Profit'][ind_l] = data_l  
        data['Long_Profit'][t: ] =  data['Long'][t: ] / data['Long'][ind_l]
        print(data['Long_Profit'][ind_l: ])
        #
        len_lp = len(data.loc[(data['Long_quotient'] > profitability), 'Long_Profit'])
        len_sp = len(data.loc[(data['Short_quotient'] > profitability), 'Short_Profit'])
        len_w = f.len_while(len_lp, len_sp)  
        print(ind_s)
        print(ind_l)
        #
    else:
        len_w = f.len_while(len_lp, len_sp) 
        print(" " * 30)
        print("Dates equal, results from positive values of both profits")
        ind = pd.date_range(data.index[0], periods = 1000, freq ='1T')
        df = pd.DataFrame(data,index = ind)
        print(ind_s)
        print(ind_l)
        print(data[ind_s: ind_s]['Short_Profit'])
        print(data[ind_l : ind_l]['Long_Profit'])
        profitability *= float(1.002)   ## Increase by commission   ##  Increase from "contractual" commission
        #
    iteator_data += 1
    time_iterator += 1    
    i += 1
    print(i)
    print("  iteator_data   =  "f'{iteator_data}')
    print(len_w)
    data.loc[(data['Long_quotient'] >= profitability ), 'Long_Profit'] = (data['Long_quotient'] - int(1))   
    data.loc[(data['Long_quotient'] < profitability ), 'Long_Profit'] = 0.0
    data.loc[(data['Short_quotient'] >= profitability ), 'Short_Profit'] = (data['Short_quotient'] - int(1)) 
    data.loc[(data['Short_quotient'] < profitability ), 'Short_Profit'] = 0.0
    print(data)
    print("end")
    #
    if data.index[-1] == ind_l == ind_s:
        print("end,   data.index[-1] == ind_l == ind_s")
        break


#######################################################################################
#
# RESULT CHARTING
#
#######################################################################################
print("We have completed the process of back-testing the pseudo rebalance")
#
data['Sum_quotient_pseudo_rebalance'] = data['Long_quotient'] + data['Short_quotient']
data['Long_quotient_after_changes'] = data['Long_quotient']
data['Short_quotient_after_changes'] = data['Short_quotient']
#
plt.title('Quotients tokens')
plt.xlabel('Time')
plt.ylabel('Quotient')
data[['Long_quotient_after_changes','Short_quotient_after_changes','The_first_sum_of_the_quotient', 'Sum_quotient_pseudo_rebalance']].plot()
plt.show()


#######################################################################################
#
# OPTIMIZATION
#
#   Use of standard deviations derived from a portfolio that uses pseudo-balancing to: ...
#   ... assess the value of the portfolio (where no balancing is performed)
#
#######################################################################################
p = 75
m = 17
d=data['Sum_quotient_pseudo_rebalance']
data['Upper_std_pseudo_rebalance'], data['Lower_std_pseudo_rebalance'] = f.upper_and_lower_standard_deviation(data=d, period=p, multiplier=m)
#
plt.title('OPTIMIZATION')
plt.xlabel('Time')
plt.ylabel('Quotient')
plt.plot(data['The_first_sum_of_the_quotient'], label = 'The first sum of the quotient', color = 'blue', markerfacecolor = 'b')
plt.plot(data['Upper_std_pseudo_rebalance'], label = 'upper band pseudo rebalance', color = 'red')
plt.plot(data['Lower_std_pseudo_rebalance'] , label = 'lower band pseudo rebalance', color = 'green')
plt.plot(data['Sum_quotient_pseudo_rebalance'], label = 'Sum quotient pseudo rebalance', color = 'black', markerfacecolor = 'k')
plt.legend()
plt.show()
# END