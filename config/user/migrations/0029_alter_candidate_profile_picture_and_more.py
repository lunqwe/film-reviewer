# Generated by Django 5.0.1 on 2024-02-10 17:47

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('user', '0028_alter_employer_banner_alter_employer_logo'),
    ]

    operations = [
        migrations.AlterField(
            model_name='candidate',
            name='profile_picture',
            field=models.ImageField(blank=True, default='defaul_icon.png', null=True, upload_to='candidate/profile_pics'),
        ),
        migrations.AlterField(
            model_name='employer',
            name='banner',
            field=models.ImageField(blank=True, default='defaul_icon.png', null=True, upload_to='./banners'),
        ),
        migrations.AlterField(
            model_name='employer',
            name='logo',
            field=models.ImageField(blank=True, default='defaul_icon.png', null=True, upload_to='./logo'),
        ),
    ]
