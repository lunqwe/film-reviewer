# Generated by Django 5.0.1 on 2024-01-25 08:38

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('user', '0006_customuser_verified_email'),
    ]

    operations = [
        migrations.AddField(
            model_name='customuser',
            name='verification_code',
            field=models.IntegerField(default=0),
        ),
    ]