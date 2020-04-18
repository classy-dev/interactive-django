from django import forms
from .models import PeriodStrategy
from django.db.models import Q
from bootstrap_datepicker_plus import DatePickerInput

class PeriodStrategyForm(forms.ModelForm):

    class Meta:
        model = PeriodStrategy
        fields = ('name',)
        widgets = {
            'name': forms.TextInput(attrs={'class': 'form-control'}),
        }

        def clean(self):
            cleaned_data = super(PeriodStrategyForm, self).clean()           
            return cleaned_data  # N'oublions pas de renvoyer les données si tout est OK    


class GeneralPeriodStrategyForm(forms.ModelForm):

    class Meta:
        model = PeriodStrategy
        fields = ('offset', 'period', 'startdate', 'enddate',)
        widgets = {
            'startdate': DatePickerInput(format='%Y-%m-%d', attrs={'onchange': 'dateEvent()'}),  # default date-format %m/%d/%Y will be used
            'enddate': DatePickerInput(format='%Y-%m-%d', attrs={'onchange': 'dateEvent()'}),  # specify date-frmat
            'offset': forms.Select(attrs={'class': 'form-control'}),
            'period': forms.Select(attrs={'class': 'form-control'}),
        }

        def clean(self):
            cleaned_data = super(GeneralCombStrategyForm, self).clean()
            return cleaned_data  # N'oublions pas de renvoyer les données si tout est OK               