from django.db import models
from polymorphic.models import PolymorphicModel
from datetime import datetime, date
from django.contrib.auth.models import User
from django.utils import timezone

# Admin Model Classes
class Input_data(models.Model):
    input_type = (
    ('instrument', 'instrument'),
    ('bench', 'bench'),
    )
    input_data = models.CharField("Input", max_length=10, choices=input_type)

    def __str__(self)-> str:
        return self.input_data


class Benchmark(models.Model):
    input_type = (
    ('^GSPTSE', 'TSX'),
    ('^G', 'SPY'),
    )
    benchmark = models.CharField("Benchmark", max_length=7, choices=input_type)

    def __str__(self)-> str:
        return self.benchmark


class Slippage(models.Model):
    input_type = (
    ('Variable', 'Variable'),
    )
    slippage = models.CharField("Slippage", max_length=8, choices=input_type)

    def __str__(self)-> str:
        return self.slippage


class Universe(models.Model):
    input_type = (
    ('Universe_Listed+Delisted', 'Universe_Listed+Delisted'),
    )
    universe = models.CharField("Universe", max_length=24, choices=input_type)

    def __str__(self)-> str:
        return self.universe


class Indicator(PolymorphicModel):
    rule_id = models.IntegerField(default=999999999)
    strategy_id = models.IntegerField()
    rank_system_id = models.IntegerField(default=0)
    liquidity_system_id = models.IntegerField(default=0)
    indicator_combination_id = models.IntegerField(default=0)
    pass

    
class Constant(Indicator):
    input_data = ""
    period = ""
    coeff = models.DecimalField(max_digits=10, decimal_places=5,default=1.0)
    lag = ""
 
    def output(self):
        return str(self.coeff)

    def __str__(self):
        return str(round(self.coeff,2))


class BarSinceEntry(Indicator):
    input_data = ""
    period = ""
    coeff = models.DecimalField(max_digits=10, decimal_places=5,default=1.0)
    lag = "" #models.IntegerField(default=0)

    def output(self):
        return "self.__barSinceEntry[instrument]*"+str(self.coeff)

    def __str__(self):
        if self.coeff != 1:
            coeff = "*"+str(round(self.coeff,2))
        else:
            coeff = ""     
        return "BarSinceEntry"+coeff


class OpenDS(Indicator):
    input_data = models.ForeignKey(Input_data, on_delete=models.CASCADE)
    period = ""
    coeff = models.DecimalField(max_digits=10, decimal_places=5,default=1.0)
    lag = models.IntegerField(default=0)

    def output(self):
        if self.lag < 0:
            lag = "(self.__barSinceEntry[instrument]-"+str(self.lag+1)+")"
        else:
            lag = str(self.lag)
        return "self.__openDS["+str(self.input_data)+"][countInstrument-"+lag+"].Value*"+str(self.coeff)

    def __str__(self):
        if self.lag < 0:
            lag = "[BarSinceEntry-"+str(self.lag+1)+"]"
        elif self.lag > 0:
            lag = "["+str(self.lag)+" days ago]"
        else:
            lag =""
        if str(self.input_data) == 'instrument' :
            input_data = ""
        else:
            input_data = "["+str(self.input_data)+"]"
        if self.coeff != 1:
            coeff = "*"+str(round(self.coeff,2))
        else:
            coeff = ""     
        return "Open" + input_data + lag + coeff


class HighDS(Indicator):
    input_data = models.ForeignKey(Input_data, on_delete=models.CASCADE)
    period = ""
    coeff = models.DecimalField(max_digits=10, decimal_places=5,default=1.0)
    lag = models.IntegerField(default=0)

    def output(self):
        if self.lag < 0:
            lag = "(self.__barSinceEntry[instrument]-"+str(self.lag+1)+")"
        else:
            lag = str(self.lag)
        return "self.__highDS["+str(self.input_data)+"][countInstrument-"+lag+"].Value*"+str(self.coeff)

    def __str__(self):
        if self.lag < 0:
            lag = "[BarSinceEntry-"+str(self.lag+1)+"]"
        elif self.lag > 0:
            lag = "["+str(self.lag)+" days ago]"
        else:
            lag =""
        if str(self.input_data) == 'instrument' :
            input_data = ""
        else:
            input_data = "["+str(self.input_data)+"]"
        if self.coeff != 1:
            coeff = "*"+str(round(self.coeff,2))
        else:
            coeff = ""     
        return "High"+input_data+lag+coeff


class LowDS(Indicator):
    input_data =models.ForeignKey(Input_data, on_delete=models.CASCADE)
    period = ""
    coeff = models.DecimalField(max_digits=10, decimal_places=5,default=1.0)
    lag = models.IntegerField(default=0)

    def output(self):
        if self.lag < 0:
            lag = "(self.__barSinceEntry[instrument]-"+str(self.lag+1)+")"
        else:
            lag = str(self.lag)
        return "self.__lowDS["+str(self.input_data)+"][countInstrument-"+lag+"].Value*"+str(self.coeff)

    def __str__(self):
        if self.lag < 0:
            lag = "[BarSinceEntry-"+str(self.lag+1)+"]"
        elif self.lag > 0:
            lag = "["+str(self.lag)+" days ago]"
        else:
            lag =""
        if str(self.input_data) == 'instrument' :
            input_data = ""
        else:
            input_data = "["+str(self.input_data)+"]"
        if self.coeff != 1:
            coeff = "*"+str(round(self.coeff,2))
        else:
            coeff = ""     
        return "Low"+input_data+lag+coeff


class PriceDS(Indicator):
    input_data = models.ForeignKey(Input_data, on_delete=models.CASCADE)
    period = ""
    coeff = models.DecimalField(max_digits=10, decimal_places=5,default=1.0)
    lag = models.IntegerField(default=0)

    def output(self):
        if self.lag < 0:
            lag = "(self.__barSinceEntry[instrument]-"+str(self.lag+1)+")"
        else:
            lag = str(self.lag)
        return "self.__priceDS["+str(self.input_data)+"][countInstrument-"+lag+"].Value*"+str(self.coeff)

    def __str__(self):
        if self.lag < 0:
            lag = "[BarSinceEntry-"+str(self.lag+1)+"]"
        elif self.lag > 0:
            lag = "["+str(self.lag)+" days ago]"
        else:
            lag =""
        if str(self.input_data) == 'instrument' :
            input_data = ""
        else:
            input_data = "["+str(self.input_data)+"]"
        if self.coeff != 1:
            coeff = "*"+str(round(self.coeff,2))
        else:
            coeff = ""     
        return "Price"+input_data+lag+coeff


class Sma(Indicator):
    input_data = models.ForeignKey(Input_data, on_delete=models.CASCADE)
    period = models.IntegerField(default=50)
    coeff = models.DecimalField(max_digits=10, decimal_places=5,default=1.0)
    lag = models.IntegerField(default=0)

    def output(self):
        if self.lag < 0:
            lag = "(self.__barSinceEntry[instrument]-"+str(self.lag+1)+")"
        else:
            lag = str(self.lag)
        return "self.__sma"+str(self.period)+"["+str(self.input_data)+"][countInstrument-"+lag+"].Value*"+str(self.coeff)

    def __str__(self):
        if self.lag < 0:
            lag = "[BarSinceEntry-"+str(self.lag+1)+"]"
        elif self.lag > 0:
            lag = "["+str(self.lag)+" days ago]"
        else:
            lag =""
        if str(self.input_data) == 'instrument' :
            input_data = ""
        else:
            input_data = "["+str(self.input_data)+"]"
        if self.coeff != 1:
            coeff = "*"+str(round(self.coeff,2))
        else:
            coeff = ""     
        return "Sma["+str(self.period)+"]" + input_data +lag + coeff

  
class Slope(Indicator):
    input_data = models.ForeignKey(Input_data, on_delete=models.CASCADE)
    period = models.IntegerField(default=20)
    coeff = models.DecimalField(max_digits=10, decimal_places=5,default=1.0)
    lag = models.IntegerField(default=0)

    def output(self):
        if self.lag < 0:
            lag = "(self.__barSinceEntry[instrument]-"+str(self.lag+1)+")"
        else:
            lag = str(self.lag)
        return "self.__slope"+str(self.period)+"["+str(self.input_data)+"][countInstrument-"+lag+"].Value*"+str(self.coeff)

    def __str__(self):
        if self.lag < 0:
            lag = "[BarSinceEntry-"+str(self.lag+1)+"]"
        elif self.lag > 0:
            lag = "["+str(self.lag)+" days ago]"
        else:
            lag =""
        if str(self.input_data) == 'instrument' :
            input_data = ""
        else:
            input_data = "["+str(self.input_data)+"]"
        if self.coeff != 1:
            coeff = "*"+str(round(self.coeff,2))
        else:
            coeff = ""     
        return "Slope["+str(self.period)+"]"+ input_data +lag + coeff

   
class Rsi(Indicator):
    input_data = models.ForeignKey(Input_data, on_delete=models.CASCADE)
    period = models.IntegerField(default=14)
    coeff = models.DecimalField(max_digits=10, decimal_places=5,default=1.0)
    lag = models.IntegerField(default=0)

    def output(self):
        if self.lag < 0:
            lag = "(self.__barSinceEntry[instrument]-"+str(self.lag+1)+")"
        else:
            lag = str(self.lag)
        return "self.__rsi"+str(self.period)+"["+str(self.input_data)+"][countInstrument-"+lag+"].Value*"+str(self.coeff)

    def __str__(self):
        if self.lag < 0:
            lag = "[BarSinceEntry-"+str(self.lag+1)+"]"
        elif self.lag > 0:
            lag = "["+str(self.lag)+" days ago]"
        else:
            lag =""
        if str(self.input_data) == 'instrument' :
            input_data = ""
        else:
            input_data = "["+str(self.input_data)+"]"
        if self.coeff != 1:
            coeff = "*"+str(round(self.coeff,2))
        else:
            coeff = ""     
        return "Rsi["+str(self.period)+"]"+ input_data +lag + coeff


class Roc(Indicator):
    input_data = models.ForeignKey(Input_data, on_delete=models.CASCADE)
    period = models.IntegerField(default=12)
    coeff = models.DecimalField(max_digits=10, decimal_places=5,default=1.0)
    lag = models.IntegerField(default=0)

    def output(self):
        if self.lag < 0:
            lag = "(self.__barSinceEntry[instrument]-"+str(self.lag+1)+")"
        else:
            lag = str(self.lag)
        return "self.__roc"+str(self.period)+"["+str(self.input_data)+"][countInstrument-"+lag+"].Value*"+str(self.coeff)

    def __str__(self):
        if self.lag < 0:
            lag = "[BarSinceEntry-"+str(self.lag+1)+"]"
        elif self.lag > 0:
            lag = "["+str(self.lag)+" days ago]"
        else:
            lag =""
        if str(self.input_data) == 'instrument' :
            input_data = ""
        else:
            input_data = "["+str(self.input_data)+"]"
        if self.coeff != 1:
            coeff = "*"+str(round(self.coeff,2))
        else:
            coeff = ""     
        return "Roc["+str(self.period)+"]"+ input_data +lag + coeff

    
class Ppo(Indicator):
    input_data = models.ForeignKey(Input_data, on_delete=models.CASCADE)
    period1 = models.IntegerField(default=12)
    period2 = models.IntegerField(default=26)
    period3 = models.IntegerField(default=9)
    coeff = models.DecimalField(max_digits=10, decimal_places=5,default=1.0)
    lag = models.IntegerField(default=0)

    def output(self):
        if self.lag < 0:
            lag = "(self.__barSinceEntry[instrument]-"+str(self.lag+1)+")"
        else:
            lag = str(self.lag)
        return "self.__ppo"+str(self.period)+"["+str(self.input_data)+"][countInstrument-"+lag+"].Value*"+str(self.coeff)

    def __str__(self):
        if self.lag < 0:
            lag = "[BarSinceEntry-"+str(self.lag+1)+"]"
        elif self.lag > 0:
            lag = "["+str(self.lag)+" days ago]"
        else:
            lag =""
        if str(self.input_data) == 'instrument' :
            input_data = ""
        else:
            input_data = "["+str(self.input_data)+"]"
        if self.coeff != 1:
            coeff = "*"+str(round(self.coeff,2))
        else:
            coeff = ""     
        return "Ppo["+str(self.period1)+"_"+str(self.period2)+"_"+str(self.period3)+"]"+ input_data +lag + coeff

    
class Ema(Indicator):
    input_data = models.ForeignKey(Input_data, on_delete=models.CASCADE)
    period = models.IntegerField(default=20)
    coeff = models.DecimalField(max_digits=10, decimal_places=5,default=1.0)
    lag = models.IntegerField(default=0)

    def output(self):
        if self.lag < 0:
            lag = "(self.__barSinceEntry[instrument]-"+str(self.lag+1)+")"
        else:
            lag = str(self.lag)
        return "self.__ema"+str(self.period)+"["+str(self.input_data)+"][countInstrument-"+lag+"].Value*"+str(self.coeff)

    def __str__(self):
        if self.lag < 0:
            lag = "[BarSinceEntry-"+str(self.lag+1)+"]"
        elif self.lag > 0:
            lag = "["+str(self.lag)+" days ago]"
        else:
            lag =""
        if str(self.input_data) == 'instrument' :
            input_data = ""
        else:
            input_data = "["+str(self.input_data)+"]"
        if self.coeff != 1:
            coeff = "*"+str(round(self.coeff,2))
        else:
            coeff = ""     
        return "Ema["+str(self.period)+"]"+ input_data +lag + coeff


class Atrn(Indicator):
    input_data = models.ForeignKey(Input_data, on_delete=models.CASCADE)
    period = models.IntegerField(default=14)
    coeff = models.DecimalField(max_digits=10, decimal_places=5,default=1.0)
    lag = models.IntegerField(default=0)

    def output(self):
        if self.lag < 0:
            lag = "(self.__barSinceEntry[instrument]-"+str(self.lag+1)+")"
        else:
            lag = str(self.lag)
        return "self.__atrn"+str(self.period)+"["+str(self.input_data)+"][countInstrument-"+lag+"].Value*"+str(self.coeff)

    def __str__(self):
        if self.lag < 0:
            lag = "[BarSinceEntry-"+str(self.lag+1)+"]"
        elif self.lag > 0:
            lag = "["+str(self.lag)+" days ago]"
        else:
            lag =""
        if str(self.input_data) == 'instrument' :
            input_data = ""
        else:
            input_data = "["+str(self.input_data)+"]"
        if self.coeff != 1:
            coeff = "*"+str(round(self.coeff,2))
        else:
            coeff = ""     
        return "Atrn["+str(self.period)+"]"+ input_data +lag + coeff

   
class Adx(Indicator):
    input_data = models.ForeignKey(Input_data, on_delete=models.CASCADE)
    period = models.IntegerField(default=14)
    coeff = models.DecimalField(max_digits=10, decimal_places=5,default=1.0)
    lag = models.IntegerField(default=0)

    def output(self):
        if self.lag < 0:
            lag = "(self.__barSinceEntry[instrument]-"+str(self.lag+1)+")"
        else:
            lag = str(self.lag)
        return "self.__adx"+str(self.period)+"["+str(self.input_data)+"][countInstrument-"+lag+"].Value*"+str(self.coeff)

    def __str__(self):
        if self.lag < 0:
            lag = "[BarSinceEntry-"+str(self.lag+1)+"]"
        elif self.lag > 0:
            lag = "["+str(self.lag)+" days ago]"
        else:
            lag =""
        if str(self.input_data) == 'instrument' :
            input_data = ""
        else:
            input_data = "["+str(self.input_data)+"]"
        if self.coeff != 1:
            coeff = "*"+str(round(self.coeff,2))
        else:
            coeff = ""     
        return "Adx["+str(self.period)+"]"+ input_data +lag + coeff

class Indicators_Combination(Indicator):
    operator_type = (
        ('+', '+'),
        ('-', '-'),
        ('*', '*'),
        ('/', '/'),
    )
    coeff = models.DecimalField(max_digits=10, decimal_places=5,default=1.0)
    indicator1 = models.ForeignKey(Indicator, related_name="indicator_comb_1", on_delete=models.CASCADE)
    operator = models.CharField("Operator", max_length=3, choices=operator_type)
    indicator2 = models.ForeignKey(Indicator, related_name="indicator_comb_2", on_delete=models.CASCADE)
    def __str__(self):
        if self.coeff != 1:
            coeff = "*"+str(round(self.coeff,2))
        else:
            coeff = ""   
        return "(" + str(self.indicator1) + str(self.operator) + str(self.indicator2) + ")" + coeff        


# User Classes
class PrimaryRule(PolymorphicModel):
    strategy_id = models.IntegerField()
    liquidity_system_id = models.IntegerField(default=0)
    pass


class Rule(PrimaryRule):
    title = models.CharField(max_length=100)
    Operator_type = (
        ('==', '=='),  # second appear in webpage
        ('<', '<'),
        ('>', '>'),
        ('<=', '<='),
        ('>=', '>='),
    )
    technical1 = models.ForeignKey(Indicator, related_name='technical_1', on_delete=models.CASCADE) #models.ManyToManyField(Indicator,related_name='technical1')
    operator = models.CharField("Operator", max_length=2, choices=Operator_type)
    technical2 = models.ForeignKey(Indicator, related_name='technical_2', on_delete=models.CASCADE) #models.ManyToManyField(Indicator,related_name='technical2')

    def output(self):
        return '('+str(self.technical1)+str(self.operator)+str(self.technical2)+')'

    def __str__(self):
        return '('+ str(self.technical1)+" "+str(self.operator)+" "+str(self.technical2)+')'

    def get_technical_id(self):
        return str(self.technical1.id) + ',' + str(self.technical2.id)

   
class RuleCombination(PrimaryRule):
    title = models.CharField(max_length=100)
    Operator_type = (
    ('and', 'and'), # second appear in webpage
    ('or', 'or'),
    ) 
    rule1 = models.ForeignKey(PrimaryRule, related_name='rule_1', on_delete=models.CASCADE)
    operator = models.CharField("Operator", max_length=3, choices=Operator_type)
    rule2 = models.ForeignKey(PrimaryRule, related_name='rule_2', on_delete=models.CASCADE)

    def output(self):
        return '('+ str(self.rule1.output())+str(self.operator)+str(self.rule2.output()) +')'

    def __str__(self):
        return '('+ str(self.rule1)+" "+str(self.operator)+" "+str(self.rule2) +')'

    def get_technical_id(self):
        return str(self.rule1.get_technical_id()) + ',' + str(self.rule2.get_technical_id())


class BuyRule(models.Model):
    buyrules = models.ForeignKey(PrimaryRule, related_name='buyrules', on_delete=models.CASCADE)
    active = models.IntegerField(default=1)
    
    def output(self):
        return self.buyrules.output() 

    def __str__(self):
        return str(self.buyrules)


class SellRule(models.Model):
    sellrules = models.ForeignKey(PrimaryRule,related_name='sellrules', on_delete=models.CASCADE)
    active = models.IntegerField(default=1)

    def output(self):
        return self.sellrules.output() 
    
    def __str__(self):
        return str(self.sellrules)


class Result(models.Model):
    strategy_id = models.IntegerField(default=0)
    Total_return = models.DecimalField(max_digits=6, decimal_places=2,default=0.0)
    Benchmark_return = models.DecimalField(max_digits=6, decimal_places=2,default=0.0)
    Annualized_return = models.DecimalField(max_digits=6, decimal_places=2,default=0.0)
    Max_drawdown = models.DecimalField(max_digits=6, decimal_places=2,default=0.0)
    Benchmark_max_drawdown = models.DecimalField(max_digits=6, decimal_places=2,default=0.0)
    pctwinners = models.DecimalField(max_digits=6, decimal_places=2,default=0.0)
    Sharpe_ratio = models.DecimalField(max_digits=6, decimal_places=2,default=0.0)
    date = models.DateField(auto_now_add=True)


class Strategy(models.Model):
    tranasction_choice = (
        ('Short', 'Short'),
        ('Long', 'Long'),
    )
    frequency_choice = (
        ('Daily', 'Daily'),
        ('Weekly', 'Weekly'),
    )
    rank_rebalance_choice = (
        ('Daily', 'Daily'),
        ('Weekly', 'Weekly'),
        ('Monthly', 'Monthly'),
        ('Never', 'Never'),
    )
    name = models.CharField(max_length=30)
    rule = models.ManyToManyField(Rule, related_name='rules+')
    rulecombination = models.ManyToManyField(RuleCombination, related_name='rulecombinations+')
    buyrule = models.ManyToManyField(BuyRule, related_name='buyrules+')
    sellrule = models.ManyToManyField(SellRule, related_name='sellrules+')
    capital = models.IntegerField(default=30000)
    positions = models.IntegerField(default=6)
    commissions = models.DecimalField(max_digits=5, decimal_places=2, default=6.99)
    benchmark = models.ForeignKey('tools.Benchmarks_Tree', on_delete=models.SET_NULL, null=True, blank=True)
    transaction_type = models.CharField("Transaction Type", max_length=10, choices=tranasction_choice,null=True, blank=True)
    frequency = models.CharField("Frequency", max_length=10, choices=frequency_choice, null=True, blank=True)
    rank_system = models.ForeignKey('tools.Ranking_System', on_delete=models.SET_NULL, null=True, blank=True)
    rank_rebalance_type = models.CharField("Ranking system rebalance", max_length=10, choices=rank_rebalance_choice, null=True, blank=True)
    liquidity_system = models.ForeignKey('tools.Liquidity_System', on_delete=models.SET_NULL, null=True, blank=True)
    universe = models.ForeignKey('tools.Universe_Tree', on_delete=models.SET_NULL, null=True, blank=True)
    datetime.strptime('1999-01-01', "%Y-%m-%d").date()
    startdate = models.DateField("StartDate", default=datetime.strptime('1999-01-01', "%Y-%m-%d").date())
    enddate = models.DateField("EndDate", default=datetime.strptime('2018-12-31', "%Y-%m-%d").date())
    results = models.OneToOneField(Result, on_delete=models.DO_NOTHING, null=True, blank=True)
    user = models.ForeignKey(User, null=True, on_delete=models.DO_NOTHING)

    state = models.CharField(default="red", max_length=10)

    class Meta:
        verbose_name = "Strategy"

    def __str__(self):
        return self.name  

    def get_rules(self):
        return self.rule.all()        

    def get_buy_rules(self):
        return self.buyrule.all()

    def get_sell_rules(self):
        return self.sellrule.all()    

    def get_rule_combinations(self):
        return self.rulecombination.all()

class Tree(models.Model):
    child_id = models.IntegerField(default=0)
    child_name = models.CharField(max_length=100)
    child_type = models.IntegerField(default=0)
    parent_id = models.IntegerField(default=0)
    permission = models.BooleanField(default=False)
    user = models.ForeignKey(User, on_delete=models.CASCADE)

class Category(models.Model):
    name = models.CharField(max_length=100)
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    path = models.CharField(max_length=200)
    def __str__(self):
        return self.name

class IndicatorProperty(models.Model):
    indicator = models.CharField(max_length=100)
    name = models.CharField(max_length=100)
    family = models.CharField(max_length=100)
    type = models.CharField(max_length=100)
    description = models.TextField(max_length=200)
    definition = models.TextField(max_length=200)

    def __str__(self):
        return self.indicator

class CombTree(models.Model):
    child_id = models.IntegerField(default=0)
    child_name = models.CharField(max_length=100)
    child_type = models.IntegerField(default=0)
    parent_id = models.IntegerField(default=0)
    permission = models.BooleanField(default=False)
    user = models.ForeignKey(User, on_delete=models.CASCADE)

class CombFolder(models.Model):
    name = models.CharField(max_length=100)
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    path = models.CharField(max_length=200)
    def __str__(self):
        return self.name

class BuyStrategy(models.Model):
    strategy = models.ForeignKey(Strategy, related_name='strategy', on_delete=models.CASCADE)
    active = models.IntegerField(default=1)
    order = models.IntegerField(default=1)

    def __str__(self):
        return str(self.strategy)

class CombinationStrategy(models.Model):
    tranasction_choice = (
        ('Short', 'Short'),
        ('Long', 'Long'),
    )
    frequency_choice = (
        ('Daily', 'Daily'),
        ('Weekly', 'Weekly'),
    )    
    name = models.CharField(max_length=100)
    capital = models.IntegerField(default=30000)
    positions = models.IntegerField(default=6)
    commissions = models.DecimalField(max_digits=5, decimal_places=2, default=6.99)
    benchmark = models.ForeignKey('tools.Benchmarks_Tree', on_delete=models.SET_NULL, null=True, blank=True)
    transaction_type = models.CharField("Transaction Type", max_length=10, null=True, blank=True, choices=tranasction_choice)
    frequency = models.CharField("Frequency", max_length=10, null=True, blank=True, choices=frequency_choice)
    universe = models.ForeignKey('tools.Universe_Tree', on_delete=models.SET_NULL, null=True, blank=True)
    datetime.strptime('1999-01-01', "%Y-%m-%d").date()
    startdate = models.DateField("StartDate", default=datetime.strptime('1999-01-01', "%Y-%m-%d").date())
    enddate = models.DateField("EndDate", default=datetime.strptime('2018-12-31', "%Y-%m-%d").date())    
    buystrategy = models.ManyToManyField(BuyStrategy, related_name='buy_strategys')
    results = models.OneToOneField(Result, on_delete=models.SET_NULL, null=True, blank=True)
    user = models.ForeignKey(User, null=True, on_delete=models.CASCADE)
    state = models.CharField(default="red", max_length=10)

    def __str__(self):
        return self.name

    def get_strategy(self):
        return self.buystrategy.all()
