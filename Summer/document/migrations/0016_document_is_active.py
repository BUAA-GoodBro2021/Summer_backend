# Generated by Django 4.0.6 on 2022-08-10 18:59

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('document', '0015_delete_documentmodel'),
    ]

    operations = [
        migrations.AddField(
            model_name='document',
            name='is_active',
            field=models.IntegerField(default=0, verbose_name='是否被编辑过'),
        ),
    ]
