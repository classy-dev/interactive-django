# Generated by Django 2.2.1 on 2019-12-04 11:01

from django.db import migrations


class Migration(migrations.Migration):

    dependencies = [
        ('optimize', '0003_auto_20191204_1830'),
    ]

    operations = [
        migrations.RenameField(
            model_name='periodstrategy',
            old_name='peroid',
            new_name='period',
        ),
    ]
