from celery import shared_task, current_task
from pyalgotrade import strategy
from pyalgotrade import barfeed
from pyalgotrade import broker
from pyalgotrade import logger
from pyalgotrade.barfeed import yahoofeed
import datetime
from pyalgotrade.utils import collections
from math import log
import operator 
import time
import numpy as np
import os
# Technical modules imported
#----------------------------
#from pyalgotrade.technical import maMultiple3
#from pyalgotrade.technical import adx4
#from pyalgotrade.technical import rsiMultiple3
#from pyalgotrade.technical import rocMultiple3
#from pyalgotrade.technical import simpleslope3
#from pyalgotrade.technical import atrn
#from pyalgotrade.technical import ppo3
from cffi import FFI
from pyalgotrade.technical_C._technical_indicators  import lib
#from pyalgotrade.technical_C._rate_of_change  import lib as _Roc
#from pyalgotrade.technical_C._average_true_range_normalised  import lib as _Atrn
#from pyalgotrade.technical_C._average_directional_index  import lib as _Adx
#from pyalgotrade.technical_C._percentage_price_oscillator  import lib as _Ppo
#from pyalgotrade.technical_C._relative_strenght_index  import lib as _Rsi
#from pyalgotrade.technical_C._simple_slope  import lib as _SimpleSlope
#from pyalgotrade.C_tools._Array import ffi, lib
import gc

class strat1(strategy.BacktestingStrategy):
    # General variables input
        #-------------------------
    def __init__(self, feed, instruments,benchmark, initialCash, positionsNumber, commission,maxlen,strategyNumber,buyrules,sellrules,RankingRebalance,rankmin):
        strategy.BacktestingStrategy.__init__(self, feed, initialCash)
        # Default variables always there
        #--------------------------------
        t0 = time.time()
        LOGGER_NAME = "broker.backtesting"
        self.__logger = logger.getLogger(LOGGER_NAME)
        self.__instruments = instruments
        self.__benchmark = benchmark
        self.__BenchCumDS = []
        self.__result_instruments = []
        self.__instrument_buy = None
        self.__positionsNumber = positionsNumber
        self.__buyrules = {}
        self.__sellrules = {}
        self.__sellRuleName = {}
        self.__buyRuleName = {}
        self.__strategyNumber = strategyNumber
        self.__rank = {}
        self.__rankmin = rankmin
        self.__barSinceEntry =  {}
        self.__count =  {}
        self.__barSinceSimulationStart =  0
        self.__longPos =  {}
        self.__currentBar = None
        self.__feed = feed
        self.__commission = commission
        self.__rebalanceRanking = None
        self.__rankFrequency = RankingRebalance # day or week or month or year or No
        self.__maxLenTechnical = 6000 # 6000 numerical variable
        self.__trades = {}
        self.__currentDateTime = 19990104
        
        # Price variables always there
        #------------------------------
        self.__priceDS =  {}
        self.__openDS =  {}
        self.__lowDS =  {}
        self.__highDS =  {}
        self.__volumeDS = {}
        self.__openDS =  {}
        self.__barDS =  {}
        self.__AvgLiquidity10 =  {} # for slippage variable
        self.__Liquidity =  {}
        self.__AvgLiquidity5 =  {}
        self.__sma5 =  {}
        self.__vma5 =  {}
        
        # Technical variables
        #---------------------
        self.__ema50 = {}
        self.__ema200 = {}
        self.__buyrules = buyrules
        self.__sellrules = sellrules
        
        # Parameter variables
        #---------------------
        
        
        #if os.path.exists("Trades.csv"):
                #os.remove("Trades.csv")
        #f = open("Trades.csv", 'a')
        #f.write("%s,%s,%s,%s,%s,%s,%s,%s \n" % ("Date","Symbol","TYPE","Shares","Price","Amount","TotFees","Note"))
        #f.close()
        
        if feed.barsHaveAdjClose():
                        self.setUseAdjustedValues(True)
        
        for instrument in self.__instruments:
                # Default variables initialisation
                #----------------------------------
                self.__sellRuleName[instrument] = ""
                self.__buyRuleName[instrument] = ""
                self.__barSinceEntry[instrument] = 0
                self.__longPos[instrument] = None
                self.__rank[instrument] = None
                self.__count[instrument] = 0
                
                # Price variables initialisation
                #--------------------------------
                self.__barDS[instrument] = feed[instrument]
                self.__priceDS[instrument] = lib.CreateArray(self.__maxLenTechnical)
                self.__openDS[instrument] = lib.CreateArray(self.__maxLenTechnical)
                self.__lowDS[instrument] = lib.CreateArray(self.__maxLenTechnical)
                self.__highDS[instrument] = lib.CreateArray(self.__maxLenTechnical)
                self.__volumeDS[instrument] = lib.CreateArray(self.__maxLenTechnical)
                self.__Liquidity[instrument] = lib.CreateArray(self.__maxLenTechnical)
                self.__AvgLiquidity5[instrument] = lib.CreateArray(self.__maxLenTechnical)
                self.__AvgLiquidity10[instrument] = lib.CreateArray(self.__maxLenTechnical)
                self.__sma5[instrument] = lib.CreateArray(self.__maxLenTechnical)
                self.__vma5[instrument] = lib.CreateArray(self.__maxLenTechnical)
                
                # Technical variables initialisation
                #------------------------------------
                self.__ema50[instrument] = lib.CreateArray(self.__maxLenTechnical)
                self.__ema200[instrument] = lib.CreateArray(self.__maxLenTechnical)
                
        # Price benchmark initialisation
        #--------------------------------
        self.__barDS[benchmark] = feed[benchmark]
        self.__priceDS[benchmark] = lib.CreateArray(self.__maxLenTechnical)
        #self.__openDS[benchmark] = collections.NumPyDeque(self.__maxLenTechnical)
        #self.__lowDS[benchmark] = collections.NumPyDeque(self.__maxLenTechnical)
        #self.__highDS[benchmark] = collections.NumPyDeque(self.__maxLenTechnical)
        #self.__BenchCumDS = collections.NumPyDeque(self.__maxLenTechnical)
       
    def onStart(self):
        process_percent = 5
        current_task.update_state(state='PROGRESS',
                                  meta={'process_percent': process_percent})

        commission = broker.backtesting.FixedPerTrade(self.__commission) # Create commission class/model 10$ per trade
        self.getBroker().setCommission(commission) # applied commission class to my broker
        #slippageModel = broker.slippage.VolumeShareSlippage()
        slippageModel = broker.slippage.SlippageVariable() # Create slippage class/model
        self.getBroker().getFillStrategy().setSlippageModel(slippageModel) # applied slippageModel
        print(("Initial portfolio value: $%.2f" % self.getBroker().getEquity()))
        print(("Maximum number of positions: %i" % self.__positionsNumber))  
        
           
    def onEnterOk(self, position):
                instrument = position.getInstrument()
                countInstrument = self.__count[instrument]-1
                execInfo = position.getEntryOrder().getExecutionInfo()
                entryInfo = position.getEntryOrder()
                filledPrice = entryInfo.getAvgFillPrice()
                Open = self.__barDS[instrument][-1].Open
                #print "BUY",self.__currentBar_Buy[instrument].getDateTime()
                slippedPrice = broker.slippage.SlippageVariable().calculatePrice(entryInfo, Open,entryInfo.getQuantity(),self.__barDS[instrument][-1], 400000, self.__AvgLiquidity10[instrument][countInstrument].Value)
                slippage_pct = (slippedPrice/Open-1)
                slippage = round(filledPrice*(-slippage_pct/(1+slippage_pct))*entryInfo.getQuantity(),2)
                Shares = entryInfo.getQuantity()
                Price = execInfo.getPrice()
                Commission = execInfo.getCommission()
                TotFees =+ Commission + abs(slippage) 
                Amount = Shares*Price - TotFees
                Date = execInfo.getDateTime()
                #self.info("BUY " + str(Shares) + " " + str(instrument) +" at " +str(round(Price,2)) + " COMMISSION " +str(Commission)+ " SLIPPAGE " + str(slippage))
                
                try:
                        self.__trades[instrument].append([Date,instrument,"BUY",Shares,round(Price,2),round(Amount,2),round(TotFees,2),self.__buyRuleName[instrument]])
                except:
                        self.__trades[instrument] = []
                        self.__trades[instrument].append([Date,instrument,"BUY",Shares,round(Price,2),round(Amount,2),round(TotFees,2),self.__buyRuleName[instrument]])
                #f = open("Trades.csv", 'a')
                #f.write("%s,%s,%s,%s,%s,%s,%s,%s \n" % (Date.strftime("%Y_%m_%d"),str(instrument),"BUY",str(Shares),str(round(Price,2)),str(Amount),str(TotFees),self.__sellRuleName[instrument]))
                #f.close()

        #        execInfo2 = self.__longPos.getEntryOrder().getAvgFillPrice()
        #        print execInfo2
                #f = open("Buy.csv", 'a')
                #f.write("Buy instrument: %s \n" % instrument)
                #f.close()
                
    def onEnterCanceled(self, position):
        if self.__longPos[position.getInstrument()] == position:
            self.__longPos[position.getInstrument()] = None
        else:
            assert(False)

    def onExitOk(self, position):
                instrument = position.getInstrument()
                countInstrument = self.__count[instrument]-1
                execInfo = position.getExitOrder().getExecutionInfo()
                exitInfo = position.getExitOrder()
                filledPrice = exitInfo.getAvgFillPrice()+10/exitInfo.getQuantity()
                Open = self.__barDS[instrument][-1].Open
                #print "SELL",self.__currentBar_Sell[instrument].getDateTime()
                slippedPrice = broker.slippage.SlippageVariable().calculatePrice(exitInfo, Open,exitInfo.getQuantity(),self.__barDS[instrument][-1], 400000, self.__AvgLiquidity10[instrument][countInstrument].Value)
                slippage_pct = (slippedPrice/Open-1)
                slippage = round(filledPrice*(slippage_pct/(1-slippage_pct))*exitInfo.getQuantity(),2)
                Shares = exitInfo.getQuantity()
                Price = execInfo.getPrice()
                Commission = execInfo.getCommission()
                TotFees =+ Commission + abs(slippage) 
                Amount = Shares*Price - TotFees
                Date = execInfo.getDateTime()
                #self.info("SELL " + str(Shares)+ " "+ str(instrument) +" at " +str(round(Price,2)) + " DUE TO " +self.__sellRuleName[instrument] + " COMMISSION " +str(Commission)+ " SLIPPAGE " + str(slippage))
                
                try:
                        self.__trades[instrument].append([Date,instrument,"SELL",Shares,round(Price,2),round(Amount,2),round(TotFees,2),self.__sellRuleName[instrument]])
                except:
                        self.__trades[instrument] = []
                        self.__trades[instrument].append([Date,instrument,"SELL",Shares,round(Price,2),round(Amount,2),round(TotFees,2),self.__sellRuleName[instrument]])
                #f = open("Trades.csv", 'a')
                #f.write("%s,%s,%s,%s,%s,%s,%s,%s \n" % (Date.strftime("%Y_%m_%d"),str(instrument),"SELL ",str(Shares),str(round(Price,2)),str(Amount),str(TotFees),self.__sellRuleName[instrument]))
                #f.close()
                #if  self.__longPos[position.getInstrument()] == position:
                #        self.__longPos[position.getInstrument()] = None
                #else:
                #        assert(False)

    def onExitCanceled(self, position):
        # If the exit was canceled, re-submit it.
        position.exitMarket()

    def onFinish(self, bars):
        print(("Final portfolio value: $%.2f" % self.getBroker().getEquity()))
        for instrument in self.__instruments:
                # Free C variables
                #----------------------------
                lib.free_Array(self.__ema50[instrument])
                lib.free_Array(self.__ema200[instrument])
                lib.free_Array(self.__priceDS[instrument])
                lib.free_Array(self.__openDS[instrument])
                lib.free_Array(self.__lowDS[instrument])
                lib.free_Array(self.__highDS[instrument])
                lib.free_Array(self.__volumeDS[instrument])
                lib.free_Array(self.__Liquidity[instrument])
                lib.free_Array(self.__AvgLiquidity5[instrument])
                lib.free_Array(self.__AvgLiquidity10[instrument])
                lib.free_Array(self.__sma5[instrument])
                lib.free_Array(self.__vma5[instrument])
        # Del variables
        #----------------------------
        del self.__ema50
        del self.__ema200
        del self.__feed
        del self.__barDS
        del self.__barSinceEntry
        del self.__longPos
        del self.__rank
        del self.__priceDS
        del self.__openDS
        del self.__lowDS
        del self.__highDS
        del self.__volumeDS
        del self.__Liquidity
        del self.__AvgLiquidity5
        del self.__AvgLiquidity10
        del self.__sma5
        del self.__vma5
        gc.collect()
        
    def getResultInstruments(self):
                return self.__result_instruments
                
    def getTrades(self):
                return self.__trades
        
    def getBenchmarkCum(self):
        return self.__BenchCumDS

    def getcurrentDateTime(self):
        return self.__currentDateTime
                
    def onBars(self, bars):
                             
                self.__barSinceSimulationStart = self.__barSinceSimulationStart + 1
                currentDateTime = bars.getDateTime()
                self.__currentDateTime = currentDateTime
                available_instruments = []         

       
                #Update Celery Process Percent
                #------------------------------
                if(self.__barSinceSimulationStart%250 == 0):
                    process_percent = int(100 * self.__barSinceSimulationStart / 5000.)
                    current_task.update_state(state='PROGRESS',
                                  meta={'process_percent': process_percent})


                # Update benchmark prices
                #------------------------
                CurrentBarBench = self.__barDS[self.__benchmark][-1]
                #print CurrentBarBench
                CurrentValueBench = CurrentBarBench.Close
                #print CurrentValueBench
                self.__priceDS[self.__benchmark][self.__barSinceSimulationStart-1].Value = CurrentValueBench
                
                # Update benchmark indicators
                #-----------------------------
                
                
                for instrument in self.__instruments:
                                try:
                                        CurrentBar = self.__barDS[instrument][-1]
                                        CurrentValue = CurrentBar.Close
                                        CurrentOpen = CurrentBar.Open
                                        CurrentLow = CurrentBar.Low
                                        CurrentHigh = CurrentBar.High
                                        CurrentVolume = CurrentBar.Volume
                                        available_instruments.append(instrument)
                                
                                except:
                                        continue # Skip instrument not yet available
                                #try:
                                        #PreviousBar = self.__barDS[instrument][-2] # for adx
                                #except:
                                        #PreviousBar = None
                                countInstrument = self.__count[instrument]
                                self.__priceDS[instrument][countInstrument].Value = CurrentValue
                                self.__openDS[instrument][countInstrument].Value = CurrentOpen
                                self.__lowDS[instrument][countInstrument].Value = CurrentLow
                                self.__highDS[instrument][countInstrument].Value = CurrentHigh
                                self.__volumeDS[instrument][countInstrument].Value = CurrentVolume
                                self.__Liquidity[instrument][countInstrument].Value = CurrentVolume*CurrentValue
                                self.__count[instrument] += 1
                                # Delete new delisted instruments
                                #---------------------------------
                                if bars.getBar(instrument) is None:
                                        self.__instruments.remove(instrument)
                                        available_instruments.remove(instrument)
                                        # Remove price variables
                                        #------------------------
                                        lib.free_Array(self.__priceDS[instrument])
                                        lib.free_Array(self.__openDS[instrument])
                                        lib.free_Array(self.__lowDS[instrument])
                                        lib.free_Array(self.__highDS[instrument])
                                        lib.free_Array(self.__volumeDS[instrument])
                                        lib.free_Array(self.__Liquidity[instrument])
                                        lib.free_Array(self.__AvgLiquidity5[instrument])
                                        lib.free_Array(self.__AvgLiquidity10[instrument])
                                        lib.free_Array(self.__sma5[instrument])
                                        lib.free_Array(self.__vma5[instrument])
                                        
                                        # Remove default variables
                                        #--------------------------
                                        del self.__barSinceEntry[instrument]
                                        del self.__longPos[instrument]
                                        del self.__rank[instrument]
                                        del self.__barDS[instrument]
                
                                        # Remove technical variables
                                        #----------------------------
                                        lib.free_Array(self.__ema50[instrument])
                                        lib.free_Array(self.__ema200[instrument])
                                         
                                        
                                        #continue # Skip the rest of the loop for this instrument
                
                for instrument in available_instruments:   
                                countInstrument = self.__count[instrument]-1                     
                                        
                                # Update price variables
                                #------------------------
                                lib.SMA(self.__Liquidity[instrument],self.__AvgLiquidity5[instrument],countInstrument,5)
                                lib.SMA(self.__Liquidity[instrument],self.__AvgLiquidity10[instrument],countInstrument,10)
                                lib.SMA(self.__priceDS[instrument],self.__sma5[instrument],countInstrument,5)
                                lib.SMA(self.__volumeDS[instrument],self.__vma5[instrument],countInstrument,5)
                                
                                # Update technical variables
                                #----------------------------
                                lib.EMA(self.__priceDS[instrument],self.__ema50[instrument],countInstrument,50)
                                lib.EMA(self.__priceDS[instrument],self.__ema200[instrument],countInstrument,200)
                                
                                        
                                
                # Wait for enough bars available
                if self.__barSinceSimulationStart <= 200:
                                self.__BenchCumDS.append(0.00)
                                return
                
                # Update benchmark cummulative return
                #-------------------------------------
                FirstValueBench = self.__priceDS[self.__benchmark][0].Value
                if FirstValueBench!= 0: 
                        benchCumm = (CurrentValueBench/FirstValueBench-1)*100.00
                else:
                        benchCumm = 0
                self.__BenchCumDS.append(benchCumm)
                
                # Ranking
                if self.__rankFrequency != "No":
                        if self._shouldRebalance(currentDateTime) or self.__barSinceSimulationStart == 201:
                                number_instruments = len(self.__instruments)
                                StockchartsScore = collections.NumPyDeque(number_instruments)
                                if self.__rankFrequency == "week":
                                        self.__rebalanceRanking = eval("currentDateTime."+"day")
                                else:
                                        self.__rebalanceRanking = eval("currentDateTime."+self.__rankFrequency)
                                for instrument in self.__instruments:
                                        countInstrument = self.__count[instrument]-1
                                        if  bars.getBar(instrument) is not None:
                                                StockchartsScore.append(-self.getStockchartsScore(instrument,countInstrument)) # to reverse argsort order
                                        else:
                                                StockchartsScore.append(10000.0)
                                
                                                
                                # Sort instruments according to ranking function        
                                indexsort = StockchartsScore.argsort()
                                sorted_instruments = []
                                for i in range(number_instruments):
                                        position = indexsort[i]
                                        sorted_instrument = self.__instruments[position]
                                        sorted_instruments.append(sorted_instrument)
                                        self.__rank[sorted_instrument] = (number_instruments-i-1)/float(number_instruments)*100.0 # fit with P123
                                        
                                self.__instruments = sorted_instruments        
                                                
                
                # Strategy core
                for instrument in available_instruments:
                        countInstrument = self.__count[instrument]-1
                        if  countInstrument >= 199 : #bars.getBar(instrument) is not None and countInstrument >= 199 :
                                
                                if self.__longPos[instrument] is not None:
                                        self.__barSinceEntry[instrument] = self.__barSinceEntry[instrument] + 1
                                        strategy = self.__longPos[instrument].getStrategyNumber()
                                        self.sellRulesCheck(strategy,self.__sellrules[strategy],instrument,countInstrument)
                                                        
                                else:
                                        for strategy in range(1,self.__strategyNumber+1):
                                                if self.buyRulesCheck(strategy,self.__buyrules[strategy],instrument,countInstrument) and self.enterLongRankingSignal(instrument) and self.__longPos[instrument] is None:
                                                        positions = len(self.getBroker().getPositions())
                                                        if         positions < self.__positionsNumber: # limited positions
                                                                buyAmount = self.getBroker().getCash()/(self.__positionsNumber-positions)
                                                                try: shares = int(buyAmount*0.95 / self.__priceDS[instrument][countInstrument].Value)
                                                                except: shares = 0.0
                                                                if self.liquidityRule2(instrument,shares,countInstrument):
                                                                        #print(instrument,self.__AvgLiquidity10[instrument][countInstrument].Value)
                                                                        self.__longPos[instrument] = self.enterLong(instrument, shares,True,True,self.__AvgLiquidity10[instrument][countInstrument].Value)
                                                                        self.__longPos[instrument].setStrategyNumber(strategy)
                                                                        #self.__logger.debug("DateTime %i" % (currentDateTime))
                                                                if instrument not in self.__result_instruments: 
                                                                                self.__result_instruments.append(instrument) 
                                                        
#-----------------------------------------------------------------------------------------------------------------
#                                                                                                Ranking
#-----------------------------------------------------------------------------------------------------------------                                                
    def _shouldRebalance(self, dateTime):
        if self.__rankFrequency == "week": # Futur work: take into account Mondays off 
            tmp =eval("dateTime."+"day")
            return  tmp != self.__rebalanceRanking and dateTime.weekday() == 0 # Rebalance on Mondays if weekly
        else:
            tmp =eval("dateTime."+self.__rankFrequency) 
            return  tmp != self.__rebalanceRanking
        

    def getStockchartsScore(self,instrument,countInstrument):        
        if countInstrument < 200: #self.__ema200[instrument][countInstrument] != self.__ema200[instrument][countInstrument] or self.__roc125[instrument][countInstrument] != self.__roc125[instrument][countInstrument]:
            return -10000.0
            #Long-Term Indicators (weighting)
        ema200Pct = ((self.__priceDS[instrument][countInstrument] - self.__ema200[instrument][countInstrument])/self.__ema200[instrument][countInstrument])*100.00
       # roc125 = self.__roc125[instrument][countInstrument]#*100.00
                
                #Medium-Term Indicators (weighting)
        #ema50Pct = ((self.__priceDS[instrument][countInstrument] - self.__ema50[instrument][countInstrument])/self.__ema50[instrument][countInstrument])*100.00
        #roc20 = self.__roc20[instrument][countInstrument]#*100.00
                
                #Short-Term Indicators (weighting)
        #slopePPO3days = self.__slopePPO3days[instrument][countInstrument]
        #rsi14 = self.__rsi14[instrument][countInstrument]
        #scoreslope = ((slopePPO3days+1)*50)*0.05
                
        score = ema200Pct#*0.3 + roc125*0.3 + ema50Pct*0.15 - roc20*0.15 - rsi14*0.05 + slopePPO3days*0.05#scoreslope
                
        return score # to reverse argsort order
        
        
    def enterLongRankingSignal(self,instrument):
                if self.__rankFrequency != "No":
                        return self.__rank[instrument] >= self.__rankmin  #or self.__rank[instrument] == None
                else:
                        return True

#-----------------------------------------------------------------------------------------------------------------
#BUY RULES
#-----------------------------------------------------------------------------------------------------------------
    # Buy rule #(self.__priceDS[instrument][countInstrument-0].Value*1.00000>20.00000) strategy #1
    #-------------------------
    def enterLongSignal5_Strategy1(self,instrument,countInstrument):
                self.__buyRuleName[instrument] = '10piece max'
                return  (self.__priceDS[instrument][countInstrument-0].Value*1.00000>20.00000) 

    # Buy rule #(self.__priceDS[instrument][countInstrument-0].Value*1.00000>self.__ema50[instrument][countInstrument-0].Value*1.00000) strategy #1
    #-------------------------
    def enterLongSignal4_Strategy1(self,instrument,countInstrument):
                self.__buyRuleName[instrument] = 'ema50'
                return  (self.__priceDS[instrument][countInstrument-0].Value*1.00000>self.__ema50[instrument][countInstrument-0].Value*1.00000) 

    # Buy rule #(self.__ema50[instrument][countInstrument-1].Value*1.00000<self.__ema200[instrument][countInstrument-1].Value*1.00000) strategy #1
    #-------------------------
    def enterLongSignal3_Strategy1(self,instrument,countInstrument):
                self.__buyRuleName[instrument] = 'emacrossover2'
                return  (self.__ema50[instrument][countInstrument-1].Value*1.00000<self.__ema200[instrument][countInstrument-1].Value*1.00000) 

    # Buy rule #(self.__ema50[instrument][countInstrument-0].Value*1.00000>self.__ema200[instrument][countInstrument-0].Value*1.00000) strategy #1
    #-------------------------
    def enterLongSignal2_Strategy1(self,instrument,countInstrument):
                self.__buyRuleName[instrument] = 'emacrossover'
                return  (self.__ema50[instrument][countInstrument-0].Value*1.00000>self.__ema200[instrument][countInstrument-0].Value*1.00000) 

    # Buy rule #(self.__priceDS[instrument][countInstrument-0].Value*1.00000>self.__ema200[instrument][countInstrument-0].Value*1.00000) strategy #1
    #-------------------------
    def enterLongSignal1_Strategy1(self,instrument,countInstrument):
                self.__buyRuleName[instrument] = 'ema200'
                return  (self.__priceDS[instrument][countInstrument-0].Value*1.00000>self.__ema200[instrument][countInstrument-0].Value*1.00000) 

                
# Buy rules check
#-----------------
    def buyRulesCheck(self,strategy,buyrules,instrument,countInstrument):
                for i in range(buyrules):
                        buyrule = "enterLongSignal{0}_Strategy{1}".format(str(i+1),strategy)
                        if not getattr(self,buyrule)(instrument,countInstrument):
                                return False
                return True
#-----------------------------------------------------------------------------------------------------------------
#                                                                                                LIQUIDIDY
#-----------------------------------------------------------------------------------------------------------------
                
# Liquidity rule #1
#------------------

    def liquidityRule1(self,instrument,shares,countInstrument):
                buyAmount = shares*self.__priceDS[instrument][countInstrument].Value
                ret = False                
                if (self.__AvgLiquidity5[instrument][countInstrument].Value) != 0:
                        pctAvgDailyTot5 = (buyAmount /(self.__AvgLiquidity5[instrument][countInstrument].Value))*100.
                else: 
                        pctAvgDailyTot5 = 100.
                if (self.__Liquidity[instrument][countInstrument].Value) != 0:
                        pctAvgDailyTot1 = (buyAmount/(self.__Liquidity[instrument][countInstrument].Value))*100.
                else: 
                        pctAvgDailyTot1 = 100.
                try: logAmout = log(buyAmount)
                except: logAmout = 0.00
                if buyAmount < 20000.:
                        if (pctAvgDailyTot5 <= (1.0687940*logAmout - 7.5691339)) and (pctAvgDailyTot1 <= (1.0687940*logAmout - 7.5691339)) and (pctAvgDailyTot1 <= 1) and (pctAvgDailyTot5 <= 1):
                                ret = True
                                #print         pctAvgDailyTot1,(1.0687940*log(buyAmount) - 7.5691339)                        
                                
                        #ret2 = [buyAmount,pctAvgDailyTot5,(1.0687940*log(buyAmount) - 7.5691339),pctAvgDailyTot1,(1.0687940*log(buyAmount) - 7.5691339)]
                        #print "ret2",ret2
                else :
                        if  (pctAvgDailyTot5 <= (0.3606738*logAmout - 0.5719281)) and (pctAvgDailyTot1 <= (0.3606738*logAmout - 0.5719281)) and (pctAvgDailyTot1 <= 1) and (pctAvgDailyTot5 <= 1):
                                ret = True
                        
                        #ret2 = [buyAmount,pctAvgDailyTot5,(0.3606738*log(buyAmount) - 0.5719281),pctAvgDailyTot1,(0.3606738*log(buyAmount) - 0.5719281)]
                        #print "ret2",ret2
                return ret

                
# Liquidity rule #2
#------------------
    def liquidityRule2(self,instrument,shares,countInstrument):
                buyAmount = shares*self.__priceDS[instrument][countInstrument].Value
                ret = False                
                if (self.__vma5[instrument][countInstrument].Value*self.__sma5[instrument][countInstrument].Value) != 0:
                        pctAvgDailyTot5 = (buyAmount /(self.__vma5[instrument][countInstrument].Value*self.__sma5[instrument][countInstrument].Value))*100.
                else: 
                        pctAvgDailyTot5 = 100.
                if (self.__Liquidity[instrument][countInstrument].Value) != 0:
                        pctAvgDailyTot1 = (buyAmount/(self.__Liquidity[instrument][countInstrument].Value))*100.
                else: 
                        pctAvgDailyTot1 = 100.
                try: logAmout = log(buyAmount)
                except: logAmout = 0.00
                if buyAmount < 20000.:
                        if (pctAvgDailyTot5 <= (1.0687940*logAmout - 7.5691339)) and (pctAvgDailyTot1 <= (1.0687940*logAmout - 7.5691339)): #and (pctAvgDailyTot1 <= 1) and (pctAvgDailyTot5 <= 1):
                                ret = True
                else :
                        if  (pctAvgDailyTot5 <= (0.3606738*logAmout - 0.5719281)) and (pctAvgDailyTot1 <= (0.3606738*logAmout - 0.5719281)):#and (pctAvgDailyTot1 <= 1) and (pctAvgDailyTot5 <= 1):
                                ret = True
                return ret

# Liquidity rule #3
#------------------
    def liquidityRule3(self,instrument,shares,countInstrument):
                buyAmount = shares*self.__priceDS[instrument][countInstrument].Value
                ret = False                
                if (self.__vma5[instrument][countInstrument].Value*self.__sma5[instrument][countInstrument].Value) != 0:
                        pctAvgDailyTot5 = (buyAmount /(self.__AvgLiquidity5[instrument][countInstrument].Value))*100.
                else: 
                        pctAvgDailyTot5 = 100.
                if (self.__Liquidity[instrument][countInstrument].Value) != 0:
                        pctAvgDailyTot1 = (buyAmount/(self.__Liquidity[instrument][countInstrument].Value))*100.
                else: 
                        pctAvgDailyTot1 = 100.
                try: logAmout = log(buyAmount)
                except: logAmout = 0.00
                if buyAmount < 20000.:
                        if (pctAvgDailyTot5 <= (1.0687940*logAmout - 7.5691339)) and (pctAvgDailyTot1 <= (1.0687940*logAmout - 7.5691339)): #and (pctAvgDailyTot1 <= 1) and (pctAvgDailyTot5 <= 1):
                                ret = True
                else :
                        if  (pctAvgDailyTot5 <= (0.3606738*logAmout - 0.5719281)) and (pctAvgDailyTot1 <= (0.3606738*logAmout - 0.5719281)):#and (pctAvgDailyTot1 <= 1) and (pctAvgDailyTot5 <= 1):
                                ret = True
                return ret
                
#-----------------------------------------------------------------------------------------------------------------
#SELL RULES
#-----------------------------------------------------------------------------------------------------------------                
    # Sell rule #((self.__ema50[instrument][countInstrument-0].Value*1.00000<self.__ema200[instrument][countInstrument-0].Value*1.00000)and(self.__ema50[instrument][countInstrument-1].Value*1.00000>self.__ema200[instrument][countInstrument-1].Value*1.00000)) strategy #1
    #-------------------------
    def exitLongSignal1_Strategy1(self,instrument,countInstrument):
                self.__sellRuleName[instrument] = 'SS'
                return  ((self.__ema50[instrument][countInstrument-0].Value*1.00000<self.__ema200[instrument][countInstrument-0].Value*1.00000)and(self.__ema50[instrument][countInstrument-1].Value*1.00000>self.__ema200[instrument][countInstrument-1].Value*1.00000)) 


                
# Sell rules check
#-----------------
    def sellRulesCheck(self,strategy,sellrules,instrument,countInstrument):
                for i in range(sellrules):
                        sellrule = "exitLongSignal{0}_Strategy{1}".format(str(i+1),strategy)
                        if getattr(self,sellrule)(instrument,countInstrument) and not self.__longPos[instrument].exitActive():
                                self.__barSinceEntry[instrument] = 0
                                self.__longPos[instrument].exitMarket(None,self.__AvgLiquidity10[instrument][countInstrument].Value)
                                self.__longPos[instrument] = None
                                return
