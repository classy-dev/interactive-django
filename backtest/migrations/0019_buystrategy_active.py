# Generated by Django 2.2.1 on 2019-11-25 04:24

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('backtest', '0018_auto_20191125_1205'),
    ]

    operations = [
        migrations.AddField(
            model_name='buystrategy',
            name='active',
            field=models.IntegerField(default=1),
        ),
    ]
