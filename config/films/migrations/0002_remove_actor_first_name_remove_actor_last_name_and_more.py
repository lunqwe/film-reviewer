# Generated by Django 5.0.2 on 2024-02-26 21:10

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('films', '0001_initial'),
    ]

    operations = [
        migrations.RemoveField(
            model_name='actor',
            name='first_name',
        ),
        migrations.RemoveField(
            model_name='actor',
            name='last_name',
        ),
        migrations.RemoveField(
            model_name='director',
            name='first_name',
        ),
        migrations.RemoveField(
            model_name='director',
            name='last_name',
        ),
        migrations.AddField(
            model_name='actor',
            name='name',
            field=models.CharField(default='', max_length=255),
        ),
        migrations.AddField(
            model_name='director',
            name='name',
            field=models.CharField(default='', max_length=255),
        ),
    ]
