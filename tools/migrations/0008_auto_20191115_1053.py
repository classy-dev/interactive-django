# Generated by Django 2.2.1 on 2019-11-15 02:53

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('tools', '0007_auto_20191111_1029'),
    ]

    operations = [
        migrations.AlterField(
            model_name='ranking_rule',
            name='direction',
            field=models.CharField(choices=[('LB', 'Lower is better'), ('HB', 'Higher is better')], max_length=20, verbose_name='Direction'),
        ),
    ]
