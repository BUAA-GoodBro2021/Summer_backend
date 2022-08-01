# Generated by Django 4.0.6 on 2022-08-01 10:50

from django.db import migrations, models


class Migration(migrations.Migration):

    initial = True

    dependencies = [
    ]

    operations = [
        migrations.CreateModel(
            name='Team',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('team_name', models.CharField(default='', max_length=30, verbose_name='团队名称')),
                ('user_num', models.IntegerField(default=0, verbose_name='成员的数量')),
                ('avatar_url', models.CharField(default='', max_length=128, verbose_name='团队头像路径')),
                ('created_time', models.DateTimeField(auto_now_add=True, verbose_name='创建时间')),
                ('updated_time', models.DateTimeField(auto_now=True, verbose_name='更新时间')),
            ],
        ),
    ]