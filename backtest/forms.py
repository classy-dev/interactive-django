from django import forms
from .models import Rule, Strategy, Indicator,RuleCombination,BuyRule,SellRule,PrimaryRule,Result, Constant,BarSinceEntry,OpenDS, HighDS, LowDS, PriceDS, Sma, Slope, Rsi, Roc, Ppo, Ema, Atrn, Adx, Indicators_Combination, CombinationStrategy
from django.db.models import Q
from bootstrap_datepicker_plus import DatePickerInput

from tools.models import Ranking_System, Liquidity_System

class RuleForm(forms.ModelForm):

    def __init__(self,strategy_id,rule_id,*args,**kwargs):
        super(RuleForm, self).__init__(*args,**kwargs) # populates the post

    class Meta:
        model = Rule
        fields = '__all__'
        exclude = ('strategy_id','liquidity_system_id')
        widgets = {
            'title': forms.TextInput(attrs={'class': 'form-control'}),
            'technical1': forms.TextInput(attrs={'class': 'form-control', 'id': 'technical_1'}),
            'operator': forms.Select(attrs={'class': 'form-control', 'id': 'operator'}),
            'technical2': forms.TextInput(attrs={'class': 'form-control', 'id': 'technical_2'}),
        }       

        def clean(self):
            cleaned_data = super(RuleForm, self).clean()           
            #if sujet and message:  # Est-ce que sujet et message sont valides ?
                #if "pizza" in sujet and "pizza" in message:
                  #  self.add_error("message", 
                    #    "Vous parlez déjà de pizzas dans le sujet, "
                    #    "n'en parlez plus dans le message !"
                    #)
            return cleaned_data  # N'oublions pas de renvoyer les données si tout est OK


class ModifyRuleForm(forms.ModelForm):

    def __init__(self,strategy_id,rule_id,*args,**kwargs):
        super(ModifyRuleForm, self).__init__(*args,**kwargs) # populates the post   

    class Meta:
        model = Rule
        fields = '__all__'
        exclude = ('strategy_id','liquidity_system_id')
        widgets = {
            'title': forms.TextInput(attrs={'class': 'form-control'}),
            'technical1': forms.TextInput(attrs={'class': 'form-control', 'id': 'technical_1'}),
            'operator': forms.Select(attrs={'class': 'form-control', 'id': 'operator'}),
            'technical2': forms.TextInput(attrs={'class': 'form-control', 'id': 'technical_2'}),
        }
        
        def clean(self):
            cleaned_data = super(ModifyRuleForm, self).clean()
            return cleaned_data  # N'oublions pas de renvoyer les données si tout est OK


class RuleCombinationForm(forms.ModelForm):

    def __init__(self,strategy_id,*args,**kwargs):
        super(RuleCombinationForm, self).__init__(*args,**kwargs) # populates the post
     
    class Meta:
        model = RuleCombination
        fields = '__all__'
        exclude = ('strategy_id','liquidity_system_id')
        widgets = {
            'title': forms.TextInput(attrs={'class': 'form-control'}),
            'rule1': forms.TextInput(attrs={'class': 'form-control', 'id': 'technical_1'}),
            'operator': forms.Select(attrs={'class': 'form-control', 'id': 'operator'}),
            'rule2': forms.TextInput(attrs={'class': 'form-control', 'id': 'technical_2'}),
        }

        def clean(self):
            cleaned_data = super(RuleCombinationForm, self).clean()           
            return cleaned_data  # N'oublions pas de renvoyer les données si tout est OK


class BuyRuleForm(forms.ModelForm):

    def __init__(self,strategy_id,*args,**kwargs):
        super(BuyRuleForm, self).__init__(*args,**kwargs) # populates the post
      
    class Meta:
        model = BuyRule
        fields = '__all__'
        widgets = {
            'buyrules': forms.TextInput(attrs={'class': 'form-control', 'id': 'buy_rule'}),
        }

        def clean(self):
            cleaned_data = super(BuyRuleForm, self).clean()           
            return cleaned_data  # N'oublions pas de renvoyer les données si tout est OK


class SellRuleForm(forms.ModelForm):

    def __init__(self,strategy_id,*args,**kwargs):
        super(SellRuleForm, self).__init__(*args,**kwargs) # populates the post
      
    class Meta:
        model = SellRule
        fields = '__all__'
        widgets = {
            'sellrules': forms.TextInput(attrs={'class': 'form-control', 'id': 'sell_rule'}),
        }
        
        def clean(self):
            cleaned_data = super(SellRuleForm, self).clean()           
            return cleaned_data


class DeleteRuleForm(forms.ModelForm):

    class Meta:
        model = Rule
        fields = ('title',)
        widgets = {
            'title': forms.TextInput(attrs={'class': 'form-control'}),
        }

        def clean(self):
            cleaned_data = super(DeleteRuleForm, self).clean()           
            return cleaned_data  # N'oublions pas de renvoyer les données si tout est OK


class StrategyForm(forms.ModelForm):

    class Meta:
        model = Strategy
        fields = ('name',)
        widgets = {
            'name': forms.TextInput(attrs={'class': 'form-control'}),
        }

        def clean(self):
            cleaned_data = super(StrategyForm, self).clean()           
            return cleaned_data  # N'oublions pas de renvoyer les données si tout est OK


class ResultForm(forms.ModelForm):

    class Meta:
        model = Result
        fields = '__all__'
        widgets = {
            'pctwinners': forms.TextInput(attrs={'class': 'form-control'}),
            'Annualized_return': forms.TextInput(attrs={'class': 'form-control'}),
            'Sharpe_ratio': forms.TextInput(attrs={'class': 'form-control'}),
        }        
       

class GeneralStrategyForm(forms.ModelForm):

    class Meta:
        model = Strategy
        fields = ('capital', 'commissions', 'positions', 'benchmark', 'universe','liquidity_system','rank_system', 'rank_rebalance_type', 'transaction_type', 'frequency','startdate', 'enddate',)
        widgets = {
            'startdate': DatePickerInput(format='%Y-%m-%d', attrs={'onchange': 'dateEvent()'}),  # default date-format %m/%d/%Y will be used
            'enddate': DatePickerInput(format='%Y-%m-%d', attrs={'onchange': 'dateEvent()'}),  # specify date-frmat
            'capital': forms.TextInput(attrs={'class': 'form-control'}),
            'commissions': forms.NumberInput(attrs={'class': 'form-control'}),
            'transaction_type': forms.Select(attrs={'class': 'form-control'}),
            'frequency': forms.Select(attrs={'class': 'form-control'}),
            'positions': forms.NumberInput(attrs={'class': 'form-control'}),
            'benchmark': forms.Select(attrs={'class': 'form-control'}),
            'rank_rebalance_type': forms.Select(attrs={'class': 'form-control'}),
            'liquidity_system': forms.Select(attrs={'class': 'form-control'}),
            'rank_system': forms.Select(attrs={'class': 'form-control'}),
            'universe': forms.Select(attrs={'class': 'form-control'}),
        }

        def clean(self):
            cleaned_data = super(StrategyForm, self).clean()
            return cleaned_data  # N'oublions pas de renvoyer les données si tout est OK

class IndicatorCombinationForm(forms.ModelForm):
    class Meta:
        model = Indicators_Combination
        fields = ('coeff', 'indicator1', 'operator', 'indicator2')
        widgets = {
            'coeff': forms.NumberInput(attrs={'class': 'form-control'}),
            'indicator1': forms.TextInput(attrs={'class': 'form-control', 'id':'indicator_1'}),
            'operator': forms.Select(attrs={'class': 'form-control'}),
            'indicator2': forms.TextInput(attrs={'class': 'form-control', 'id':'indicator_2'}),
        }            

class CombinationStrategyForm(forms.ModelForm):

    class Meta:
        model = CombinationStrategy
        fields = ('name',)
        widgets = {
            'name': forms.TextInput(attrs={'class': 'form-control'}),
        }

        def clean(self):
            cleaned_data = super(CombinationStrategyForm, self).clean()           
            return cleaned_data  # N'oublions pas de renvoyer les données si tout est OK        

class GeneralCombStrategyForm(forms.ModelForm):

    class Meta:
        model = CombinationStrategy
        fields = ('capital', 'commissions', 'positions', 'benchmark', 'universe', 'transaction_type', 'frequency','startdate', 'enddate',)
        widgets = {
            'startdate': DatePickerInput(format='%Y-%m-%d', attrs={'onchange': 'dateEvent()'}),  # default date-format %m/%d/%Y will be used
            'enddate': DatePickerInput(format='%Y-%m-%d', attrs={'onchange': 'dateEvent()'}),  # specify date-frmat
            'capital': forms.TextInput(attrs={'class': 'form-control'}),
            'commissions': forms.NumberInput(attrs={'class': 'form-control'}),
            'transaction_type': forms.Select(attrs={'class': 'form-control'}),
            'frequency': forms.Select(attrs={'class': 'form-control'}),
            'positions': forms.NumberInput(attrs={'class': 'form-control'}),
            'benchmark': forms.Select(attrs={'class': 'form-control'}),
            'universe': forms.Select(attrs={'class': 'form-control'}),
        }

        def clean(self):
            cleaned_data = super(GeneralCombStrategyForm, self).clean()
            return cleaned_data  # N'oublions pas de renvoyer les données si tout est OK            