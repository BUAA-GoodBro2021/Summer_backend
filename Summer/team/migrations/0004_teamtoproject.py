# Generated by Django 4.0.6 on 2022-08-01 16:24

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('team', '0003_team_project_num'),
    ]

    operations = [
        migrations.CreateModel(
            name='TeamToProject',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('team_id', models.IntegerField(default=0, verbose_name='团队id')),
                ('project_id', models.IntegerField(default=0, verbose_name='项目id')),
            ],
        ),
    ]