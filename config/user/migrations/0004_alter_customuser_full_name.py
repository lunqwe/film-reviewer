# Generated by Django 5.0.1 on 2024-01-22 21:03

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('user', '0003_alter_customuser_full_name'),
    ]

    operations = [
        migrations.AlterField(
            model_name='customuser',
            name='full_name',
            field=models.CharField(blank=True, default='', max_length=255, null=True),
        ),
    ]