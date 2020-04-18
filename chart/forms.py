from django import forms
from chart.models import (Chart,  Instrument, List)


class ChartForm(forms.ModelForm):

    class Meta:
        model = Chart
        fields = ['name', 'type', 'decreasing_color', 'increasing_color', 'line_color']
        widgets = {
            'name': forms.TextInput(attrs={'class': 'form-control'}),
            'type': forms.Select(attrs={'class': 'form-control'}),
            'decreasing_color': forms.Select(attrs={'class': 'form-control'}),
            'increasing_color': forms.Select(attrs={'class': 'form-control'}),
            'line_color': forms.Select(attrs={'class': 'form-control'}),
        }

    def clean(self):
        cleaned_data = super(ChartForm, self).clean()


class ListForm(forms.ModelForm):
    class Meta:
        model = List
        fields = ('name',)
        widgets = {
            'name': forms.TextInput(attrs={'class': 'form-control'}),
        }


class ListDeleteForm(forms.ModelForm):
    class Meta:
        model = List
        fields = ('name',)
        widgets = {
            'name': forms.TextInput(attrs={'class': 'form-control'}),
        }


class InstrumentForm(forms.ModelForm):
    class Meta:
        model = Instrument
        fields = ('name',)
        exclude = ('list_id', 'chart_id')
        widgets = {
            'name': forms.TextInput(attrs={'class': 'form-control'}),
        }


class InstrumentDeleteForm(forms.ModelForm):
    class Meta:
        model = Instrument
        fields = ('name',)
        widgets = {
            'name': forms.TextInput(attrs={'class': 'form-control'}),
        }


class ChartDeleteForm(forms.ModelForm):
    class Meta:
        model = Chart
        fields = ('name',)
        widgets = {
            'name': forms.TextInput(attrs={'class': 'form-control'}),
        }


class ListNameModifyForm(forms.ModelForm):
    class Meta:
        model = List
        fields = ('name',)
        widgets = {
            'name': forms.TextInput(attrs={'class': 'form-control'}),
        }
