# Generated by Django 2.2.1 on 2019-11-07 14:51

from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        ('tools', '0003_auto_20191107_1950'),
        ('backtest', '0007_auto_20191107_1950'),
    ]

    operations = [
        migrations.AddField(
            model_name='strategy',
            name='liquidity_system',
            field=models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.CASCADE, to='tools.Liquidity_System'),
        ),
        migrations.AddField(
            model_name='strategy',
            name='rank_system',
            field=models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.CASCADE, to='tools.Ranking_System'),
        ),
    ]
