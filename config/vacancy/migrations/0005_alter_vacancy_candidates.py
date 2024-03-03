# Generated by Django 5.0.1 on 2024-02-29 22:20

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('user', '0040_alter_employer_banner_alter_employer_logo'),
        ('vacancy', '0004_vacancy_candidates_vacancy_status_and_more'),
    ]

    operations = [
        migrations.AlterField(
            model_name='vacancy',
            name='candidates',
            field=models.ManyToManyField(blank=True, related_name='candidates', to='user.candidate'),
        ),
    ]
