from django.contrib import admin
from chart.models import Chart, List, Instrument, ChartType, ChartOverlay, ChartIndicator

# Register your models here.
admin.site.register(Chart)
admin.site.register(List)
admin.site.register(Instrument)
admin.site.register(ChartType)
admin.site.register(ChartOverlay)
admin.site.register(ChartIndicator)
