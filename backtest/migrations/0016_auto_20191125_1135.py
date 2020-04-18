# Generated by Django 2.2.1 on 2019-11-25 03:35

from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        ('backtest', '0015_combinationstrategy_results'),
    ]

    operations = [
        migrations.CreateModel(
            name='SubField',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('active', models.BooleanField(default=1)),
            ],
        ),
        migrations.RemoveField(
            model_name='combinationstrategy',
            name='strategy',
        ),
        migrations.AddField(
            model_name='combinationstrategy',
            name='strategy',
            field=models.ManyToManyField(through='backtest.SubField', to='backtest.Strategy'),
        ),        
        migrations.AddField(
            model_name='subfield',
            name='combinationstrategy',
            field=models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='backtest.CombinationStrategy'),
        ),
        migrations.AddField(
            model_name='subfield',
            name='strategy',
            field=models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='backtest.Strategy'),
        ),
    ]
