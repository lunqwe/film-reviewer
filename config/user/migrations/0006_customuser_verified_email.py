# Generated by Django 5.0.1 on 2024-01-24 20:30

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('user', '0005_alter_customuser_status'),
    ]

    operations = [
        migrations.AddField(
            model_name='customuser',
            name='verified_email',
            field=models.BooleanField(default=False),
        ),
    ]
