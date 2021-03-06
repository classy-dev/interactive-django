# Generated by Django 2.2.1 on 2019-11-16 15:23

import datetime
from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        ('backtest', '0012_combinationstrategy'),
    ]

    operations = [
        migrations.AddField(
            model_name='combinationstrategy',
            name='benchmark',
            field=models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.CASCADE, to='backtest.Benchmark'),
        ),
        migrations.AddField(
            model_name='combinationstrategy',
            name='capital',
            field=models.IntegerField(default=30000),
        ),
        migrations.AddField(
            model_name='combinationstrategy',
            name='commissions',
            field=models.DecimalField(decimal_places=2, default=6.99, max_digits=5),
        ),
        migrations.AddField(
            model_name='combinationstrategy',
            name='enddate',
            field=models.DateField(default=datetime.date(2018, 12, 31), verbose_name='EndDate'),
        ),
        migrations.AddField(
            model_name='combinationstrategy',
            name='frequency',
            field=models.CharField(choices=[('Daily', 'Daily'), ('Weekly', 'Weekly')], default=0, max_length=10, verbose_name='Frequency'),
            preserve_default=False,
        ),
        migrations.AddField(
            model_name='combinationstrategy',
            name='positions',
            field=models.IntegerField(default=6),
        ),
        migrations.AddField(
            model_name='combinationstrategy',
            name='startdate',
            field=models.DateField(default=datetime.date(1999, 1, 1), verbose_name='StartDate'),
        ),
        migrations.AddField(
            model_name='combinationstrategy',
            name='transaction_type',
            field=models.CharField(choices=[('Short', 'Short'), ('Long', 'Long')], default=0, max_length=10, verbose_name='Transaction Type'),
            preserve_default=False,
        ),
        migrations.AddField(
            model_name='combinationstrategy',
            name='universe',
            field=models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.CASCADE, to='backtest.Universe'),
        ),
    ]
