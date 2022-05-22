#!/usr/bin/env python3

import math
import time
import json
import random
import yfinance as yf
import pandas as pd
import sys
import random
from datetime import date, timedelta
from pandas_datareader import data as pdr
# override yfinance with pandas – seems to be a common step


def ectract_data():
    yf.pdr_override()
    # Get stock data from Yahoo Finance – here, asking for about 10 years of Amazon
    today = date.today()
    decadeAgo = today - timedelta(days=3652)
    
    data = pdr.get_data_yahoo('AMZN', start=decadeAgo, end=today).reset_index() 
    # Other symbols: CSCO – Cisco, NFLX – Netflix, INTC – Intel, TSLA - Tesla 
    data["Date"] = data["Date"].apply(lambda x: pd.Timestamp(x).date().strftime('%m/%d/%Y'))
    
    data['Buy']=0
    data['Sell']=0
    
    for i in range(len(data)): 
        # Hammer
        realbody=math.fabs(data.Open[i]-data.Close[i])
        bodyprojection=0.1*math.fabs(data.Close[i]-data.Open[i])
        if data.High[i] >= data.Close[i] and data.High[i]-bodyprojection <= data.Close[i] and data.Close[i] > data.Open[i] and data.Open[i] > data.Low[i] and data.Open[i]-data.Low[i] > realbody:
            data.at[data.index[i], 'Buy'] = 1
        #print("H", data.Open[i], data.High[i], data.Low[i], data.Close[i])   

    # Inverted Hammer
    if data.High[i] > data.Close[i] and data.High[i]-data.Close[i] > realbody and data.Close[i] > data.Open[i] and data.Open[i] >= data.Low[i] and data.Open[i] <= data.Low[i]+bodyprojection:
        data.at[data.index[i], 'Buy'] = 1
        #print("I", data.Open[i], data.High[i], data.Low[i], data.Close[i])

    # Hanging Man
    if data.High[i] >= data.Open[i] and data.High[i]-bodyprojection <= data.Open[i] and data.Open[i] > data.Close[i] and data.Close[i] > data.Low[i] and data.Close[i]-data.Low[i] > realbody:
        data.at[data.index[i], 'Sell'] = 1
        #print("M", data.Open[i], data.High[i], data.Low[i], data.Close[i])

    # Shooting Star
    if data.High[i] > data.Open[i] and data.High[i]-data.Open[i] > realbody and data.Open[i] > data.Close[i] and data.Close[i] >= data.Low[i] and data.Close[i] <= data.Low[i]+bodyprojection:
        data.at[data.index[i], 'Sell'] = 1
        #print("S", data.Open[i], data.High[i], data.Low[i], data.Close[i])
        
    return data

def calculation_EC2(history,shots,sigal):
    val=[]
    elp=time.time()
    exct_data=ectract_data()
    minhistory = history
    shots = shots
    for i in range(minhistory, len(exct_data)): 
        if exct_data.Buy[i]==1: # if we’re interested in Buy signals
                mean=exct_data.Close[i-minhistory:i].pct_change(1).mean()
                std=exct_data.Close[i-minhistory:i].pct_change(1).std()
                # generate much larger random number series with same broad characteristics 
                simulated = [random.gauss(mean,std) for x in range(shots)]
                # sort and pick 95% and 99%  - not distinguishing long/short here
                simulated.sort(reverse=True)
                var95 = simulated[int(len(simulated)*0.95)]
                var99 = simulated[int(len(simulated)*0.99)]

                #print(var95, var99) # so you can see what is being produced
                val.append([str(exct_data['Date'][i]),var95, var99])
    elp_time=str(time.time() - elp)
    
    
    return json.dumps({
        "val_risk":val,
        "Elp_time": elp_time,
    })
    
    
    
sys.stdout.write(calculation_EC2(int(sys.argv[1]),int(sys.argv[2]),int(sys.argv[3])))
