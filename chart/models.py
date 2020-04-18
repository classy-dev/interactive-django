from django.db import models
from django.contrib.auth.models import User
from chart.choices import (period_choice, color_choice, position_choice)


class ChartType (models.Model):
    type = models.CharField(max_length=20)

    def __str__(self):
        return self.type

    def output(self):
        return self.type


class ChartOverlay (models.Model):
    type = models.CharField(max_length=200)
    name = models.CharField(max_length=200)
    param = models.IntegerField(default=0)

    def __str__(self):
        return self.type

    def output(self):
        return self.type


class ChartIndicator (models.Model):
    type = models.CharField(max_length=200)
    name = models.CharField(max_length=200)
    param = models.IntegerField(default=0)
    position = models.CharField(max_length=20, choices=position_choice)

    def __str__(self):
        return self.type

    def output(self):
        return self.type


class Chart (models.Model):
    name = models.CharField(max_length=200)
    type = models.ForeignKey(ChartType, on_delete=models.CASCADE)
    decreasing_color = models.CharField(max_length=20, choices=color_choice)
    increasing_color = models.CharField(max_length=20, choices=color_choice)
    line_color = models.CharField(max_length=20, choices=color_choice)
    period = models.CharField(max_length=30, choices=period_choice, default='d')
    overlay = models.ManyToManyField(ChartOverlay)
    indicator = models.ManyToManyField(ChartIndicator)
    user = models.ForeignKey(User, null=True, on_delete=models.DO_NOTHING)

    class Meta:
        verbose_name = "Chart"

    def __str__(self):
        return self.name

    def output(self):
        return self.name



class List (models.Model):
    name = models.CharField(max_length=50)
    chart = models.ForeignKey(Chart, on_delete=models.CASCADE)

    class Meta:
        verbose_name = "List"

    def __str__(self):
        return self.name

    def output(self):
        return self.name


class Instrument (models.Model):
    name = models.CharField(max_length=50)
    active = models.BooleanField(null=True)
    universe = models.CharField(max_length=50)
    list = models.ForeignKey(List, on_delete=models.CASCADE)
    chart = models.ForeignKey(Chart, on_delete=models.DO_NOTHING)

    class Meta:
        verbose_name = "Instrument"

    def __str__(self):
        return self.name

    def output(self):
        return self.name

