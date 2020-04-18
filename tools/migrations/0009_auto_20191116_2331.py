# Generated by Django 2.2.1 on 2019-11-16 15:31

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('tools', '0008_auto_20191115_1053'),
    ]

    operations = [
        migrations.AlterField(
            model_name='ranking_rule',
            name='direction',
            field=models.CharField(choices=[('HB', 'Higher is better'), ('LB', 'Lower is better')], max_length=20, verbose_name='Direction'),
        ),
    ]