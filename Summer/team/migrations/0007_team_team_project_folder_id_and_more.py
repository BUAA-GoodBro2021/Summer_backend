# Generated by Django 4.0.6 on 2022-08-07 19:53

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('team', '0006_team_team_folder_id'),
    ]

    operations = [
        migrations.AddField(
            model_name='team',
            name='team_project_folder_id',
            field=models.IntegerField(default=0, verbose_name='项目文档区'),
        ),
        migrations.AlterField(
            model_name='team',
            name='team_folder_id',
            field=models.IntegerField(default=0, verbose_name='文档中心'),
        ),
    ]
