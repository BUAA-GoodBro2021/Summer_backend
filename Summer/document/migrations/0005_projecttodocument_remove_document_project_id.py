# Generated by Django 4.0.6 on 2022-08-02 14:17

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('document', '0004_document_project_id'),
    ]

    operations = [
        migrations.CreateModel(
            name='ProjectToDocument',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('project_id', models.IntegerField(default=0, verbose_name='项目id')),
                ('document_id', models.IntegerField(default=0, verbose_name='文档id')),
            ],
        ),
        migrations.RemoveField(
            model_name='document',
            name='project_id',
        ),
    ]