# Generated by Django 4.0.6 on 2022-08-03 10:57

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('project', '0002_project_project_description'),
    ]

    operations = [
        migrations.AddField(
            model_name='project',
            name='avatar_url',
            field=models.CharField(default='', max_length=128, verbose_name='项目头像路径'),
        ),
    ]
