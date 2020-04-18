import django_filters

from backtest.models import Rule, Indicator

class RuleFilter(django_filters.FilterSet):
        class Meta:
            model = Rule
            fields = ['technical1']