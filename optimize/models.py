from django.db import models
from django.contrib.auth.models import User
from datetime import datetime, date
# Create your models here.

class PeriodTree(models.Model):
    child_id = models.IntegerField(default=0)
    child_name = models.CharField(max_length=100)
    child_type = models.IntegerField(default=0)
    parent_id = models.IntegerField(default=0)
    permission = models.BooleanField(default=False)
    user = models.ForeignKey(User, on_delete=models.CASCADE)

class PeriodFolder(models.Model):
    name = models.CharField(max_length=100)
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    path = models.CharField(max_length=200)
    def __str__(self):
        return self.name

class Result(models.Model):
    Total_return = models.DecimalField(max_digits=6, decimal_places=2,default=0.0)
    Benchmark_return = models.DecimalField(max_digits=6, decimal_places=2,default=0.0)
    Annualized_return = models.DecimalField(max_digits=6, decimal_places=2,default=0.0)
    Max_drawdown = models.DecimalField(max_digits=6, decimal_places=2,default=0.0)
    Benchmark_max_drawdown = models.DecimalField(max_digits=6, decimal_places=2,default=0.0)
    pctwinners = models.DecimalField(max_digits=6, decimal_places=2,default=0.0)
    Sharpe_ratio = models.DecimalField(max_digits=6, decimal_places=2,default=0.0)
    date = models.DateField(auto_now_add=True)        

class PeriodStrategy(models.Model): 
    name = models.CharField(max_length=100)
    offset_choice = (
        ('day', 'day'),
        ('week', 'week'),
        ('month', 'month'),
    )
    period_choice = (
        ('6 months', '6 months'),
        ('1 year', '1 year'),
        ('2 year', '2 year'),
    )
    offset = models.CharField("Offset", max_length=20, null=True, blank=True, choices=offset_choice)
    period = models.CharField("Period", max_length=20, null=True, blank=True, choices=period_choice)    
    startdate = models.DateField("StartDate", default=datetime.strptime('1999-01-01', "%Y-%m-%d").date())
    enddate = models.DateField("EndDate", default=datetime.strptime('2018-12-31', "%Y-%m-%d").date())    
    strategy = models.OneToOneField('backtest.Strategy', related_name='period_strategy', null=True, blank=True, on_delete=models.SET_NULL)
    results = models.OneToOneField(Result, on_delete=models.SET_NULL, null=True, blank=True)
    user = models.ForeignKey(User, null=True, on_delete=models.CASCADE)

    def __str__(self):
        return self.name    