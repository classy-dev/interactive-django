# Generated by Django 2.2.1 on 2019-11-26 02:40

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('backtest', '0023_auto_20191126_0207'),
    ]

    operations = [
        migrations.RemoveField(
            model_name='ppo',
            name='period',
        ),
        migrations.AddField(
            model_name='ppo',
            name='period1',
            field=models.IntegerField(default=12),
        ),
        migrations.AddField(
            model_name='ppo',
            name='period2',
            field=models.IntegerField(default=26),
        ),
        migrations.AddField(
            model_name='ppo',
            name='period3',
            field=models.IntegerField(default=9),
        ),
    ]
