# Generated by Django 2.2.1 on 2019-11-07 11:50

from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        ('backtest', '0006_auto_20191107_1949'),
    ]

    operations = [
        migrations.AlterField(
            model_name='rulecombination',
            name='rule1',
            field=models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='rule_1', to='backtest.PrimaryRule'),
        ),
        migrations.AlterField(
            model_name='rulecombination',
            name='rule2',
            field=models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='rule_2', to='backtest.PrimaryRule'),
        ),
    ]
