# Generated by Django 4.1 on 2022-08-09 20:49

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('page', '0009_modeltopage_model_name'),
    ]

    operations = [
        migrations.CreateModel(
            name='ProjectModel',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('project_id', models.IntegerField(default=0, verbose_name='项目id')),
                ('model_name', models.CharField(default='', max_length=100, verbose_name='页面名称')),
            ],
        ),
        migrations.RemoveField(
            model_name='modeltopage',
            name='model_name',
        ),
        migrations.RemoveField(
            model_name='modeltopage',
            name='project_id',
        ),
        migrations.AddField(
            model_name='modeltopage',
            name='model_id',
            field=models.IntegerField(default=0, verbose_name='模板id'),
        ),
    ]
