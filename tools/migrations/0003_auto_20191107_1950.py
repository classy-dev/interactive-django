# Generated by Django 2.2.1 on 2019-11-07 11:50

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('tools', '0002_auto_20191105_1118'),
    ]

    operations = [
        migrations.AlterField(
            model_name='ranking_rule',
            name='direction',
            field=models.CharField(choices=[('LB', 'Lower is better'), ('HB', 'Higher is better')], max_length=20, verbose_name='Direction'),
        ),
    ]
