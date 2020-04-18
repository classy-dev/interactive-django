from django.contrib import admin
from .models import Input_data,Indicator, Strategy, Rule, Benchmark, Universe

admin.site.register(Input_data)
admin.site.register(Universe)
admin.site.register(Benchmark)
admin.site.register(Indicator)
admin.site.register(Rule)
admin.site.register(Strategy)