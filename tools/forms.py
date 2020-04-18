from django import forms

from .models import Universe_Default, Lists_Default, Benchmarks_Default, Ranking_System, Ranking_Rule, Liquidity_System, Liquidity_Rule
                    # Indicators_Combination, Indicators_Combination_System

class UniverseForm(forms.ModelForm):
    class Meta:
        model = Universe_Default
        fields = ('file',)

class ListForm(forms.ModelForm):
    class Meta:
        model = Lists_Default
        fields = ('file',)

class BenchmarkForm(forms.ModelForm):
    class Meta:
        model = Benchmarks_Default
        fields = ('file',)

class RankingSystemForm(forms.ModelForm):
    class Meta:
        model = Ranking_System
        fields = ('name',)
        widgets = {
            'name': forms.TextInput(attrs={'class': 'form-control'}),
        }
        def clean(self):
            cleaned_data = super(RankingSystemForm, self).clean()           
            return cleaned_data 

class RankingRuleForm(forms.ModelForm):
    class Meta:
        model = Ranking_Rule
        fields = '__all__'
        exclude = ('rank_id',)
        widgets = {
            'weight': forms.NumberInput(attrs={'class':'form-control'}),
            'indicator': forms.TextInput(attrs={'class':'form-control','id':'indicator'}),
            'name': forms.TextInput(attrs={'class':'form-control'}),
            'direction': forms.Select(attrs={'class':'form-control'}),
        }
        def clean(self):
            cleaned_data = super(RankingRuleForm, self).clean()           
            return cleaned_data 

#LIQUIDITY SYSTEM
class LiquiditySystemForm(forms.ModelForm):
    class Meta:
        model = Liquidity_System
        fields = ('name',)
        widgets = {
            'name': forms.TextInput(attrs={'class': 'form-control'}),
        }
        def clean(self):
            cleaned_data = super(LiquiditySystemForm, self).clean()           
            return cleaned_data 

class LiquidityRuleForm(forms.ModelForm):
    class Meta:
        model = Liquidity_Rule
        fields = '__all__'
        widgets = {
            'min_amount': forms.NumberInput(attrs={'class':'form-control'}),
            'max_amount': forms.NumberInput(attrs={'class':'form-control'}),
            'rule': forms.TextInput(attrs={'class':'form-control', 'id':'liquidity_rule'}),
            'name': forms.TextInput(attrs={'class':'form-control'}),
        }
        def clean(self):
            cleaned_data = super(LiquidityRuleForm, self).clean()           
            return cleaned_data 