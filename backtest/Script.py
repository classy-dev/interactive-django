from celery import shared_task, current_task
import os
import datetime
import time
import sys
import pickle
import random
from numpy import random


@shared_task
def interactive_process(userpath):

    #load strategy
    with open(userpath+'/inputs.pickle', 'rb') as f:
       strategy = pickle.load(f)

    Results = {}
    Results["invested"] = []
    Results["Cummulative_returns"] = []
    Results["Benchmark_return"] = []
    Results["DrawDown"] = []
    Results["Annual_returns"] = []

    base = datetime.datetime.today().date()
    numdays = 200*10
    date_list = [base - datetime.timedelta(days=x) for x in range(0, numdays)]

    # Do something and get results
    i = 0
    for date in date_list:
        i = i + 1
        x = random.normal(0, 0.1, 2000)
        if(i%30 == 0):
            process_percent = int(100 * float(i) / float(len(date_list)))
            current_task.update_state(state='PROGRESS',
                                      meta={'process_percent': process_percent})
        Results["invested"].append([str(date), random.randint(0, 100)])
        Results["Cummulative_returns"].append([str(date),random.randint(0,100)])
        Results["Benchmark_return"].append([str(date),random.randint(0,100)])
        Results["DrawDown"].append([str(date),random.randint(0,100)])
        Results["Annual_returns"].append([str(date),random.randint(0,100)])
       

    Results["Total_Return"] = 55.0
    Results["Benchmark_Return"] = 7.0
    Results["Annualized_Return"] = 12.02
    Results["Max_Drowdown"] = 6.36
    Results["Benchmark_Max_Drowdown"] = 12.50
    Results["Winner_Percentage"] = 86.65
    Results["Sharpe_Ratio"] = -1.26

    instrumentList = ["BBD.B","FFH","VFF","GCE","ZYME","ZZZ"]
    RuleNameList = ["BR1","BR2","BR3","BR4","BR5"]
   
    Results["Trades"] = []

    for i in range(30):
        Date = random.choice(date_list)
        x = random.randint(1,30)
        DateSell = Date + datetime.timedelta(days=x)
        instrument = random.choice(instrumentList)
        Shares = random.randint(1,21)*50
        Price = random.random()*10
        PriceSell = random.random()*10
        TotFees = 10.0
        Amount = Shares*Price + TotFees
        AmountSell = Shares*PriceSell + TotFees
        RuleName = random.choice(RuleNameList)
        Results["Trades"].append([str(Date),instrument,"BUY",Shares,round(Price,2),round(Amount,2),round(TotFees,2),RuleName,str(DateSell),instrument,"SELL",Shares,round(PriceSell,2),round(AmountSell,2),round(TotFees,2),"SR1"])
    with open(userpath+'/Results.pickle', 'wb') as f:
            pickle.dump(Results, f, protocol= 2)

    flag = False
    while flag is False:
        flag = os.path.isfile(userpath+'/Results.pickle')
    
    return random.random()